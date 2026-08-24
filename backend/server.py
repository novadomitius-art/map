from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import json
import logging
import copy
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Tuple, Optional
from datetime import datetime, timezone

from map_ops import transfer_territory, apply_trace, rings_to_shape, shape_to_rings
from shapely.ops import unary_union
from shapely.validation import make_valid


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

# ------------- world state (in-memory, seeded from world_data.json) ------
WORLD_PATH = ROOT_DIR / "world_data.json"
TRACE_PATH = ROOT_DIR / "trace_overrides.json"
SEED_WORLD = json.loads(WORLD_PATH.read_text())
STATE = {
    "nations": copy.deepcopy(SEED_WORLD["nations"]),
    "provinces": copy.deepcopy(SEED_WORLD["provinces"]),
    "settlements": copy.deepcopy(SEED_WORLD["settlements"]),
    "religions": copy.deepcopy(SEED_WORLD["religions"]),
    "relations": copy.deepcopy(SEED_WORLD["relations"]),
    "continent": SEED_WORLD["continent"],
    "current_year": SEED_WORLD["current_year"],
    "lore": SEED_WORLD["lore"],
}

TRACES: list = []
if TRACE_PATH.exists():
    try:
        TRACES = json.loads(TRACE_PATH.read_text())
    except Exception:
        TRACES = []


def _save_traces():
    TRACE_PATH.write_text(json.dumps(TRACES))


def _apply_all_traces():
    """Re-apply saved trace overrides onto STATE (used at startup and reset)."""
    for t in TRACES:
        try:
            provs, setts, _ = apply_trace(
                STATE["provinces"], STATE["settlements"],
                t["type"], t["polygon"], t.get("value"),
            )
            STATE["provinces"] = provs
            STATE["settlements"] = setts
        except Exception as e:
            logging.getLogger(__name__).warning(f"Trace {t.get('id')} failed to reapply: {e}")


_apply_all_traces()


# ------------- nation shapes (smooth merged territories) ------------------
NATION_SHAPES = {"dirty": True, "data": {}}


def _mark_shapes_dirty():
    NATION_SHAPES["dirty"] = True


def _compute_nation_shapes():
    """Merged + smoothed territory outline per nation (soft organic borders)."""
    by_nation = {}
    for p in STATE["provinces"]:
        by_nation.setdefault(p["nation_id"], []).append(rings_to_shape(p["polygons"]))
    out = {}
    for nid, geoms in by_nation.items():
        gs = [g for g in geoms if g is not None]
        if not gs:
            continue
        u = make_valid(unary_union(gs))
        sm = u.simplify(0.0008).buffer(0.0035, join_style=1, quad_segs=3).buffer(
            -0.0035, join_style=1, quad_segs=3)
        sm = make_valid(sm)
        out[nid] = shape_to_rings(sm if not sm.is_empty else u)
    return out


def _nation_shapes():
    if NATION_SHAPES["dirty"]:
        NATION_SHAPES["data"] = _compute_nation_shapes()
        NATION_SHAPES["dirty"] = False
    return NATION_SHAPES["data"]


def _relations_for(nation_id):
    return [r for r in STATE["relations"] if r["a"] == nation_id or r["b"] == nation_id]


def _vassals_of(overlord_id):
    return [n for n in STATE["nations"] if n.get("overlord") == overlord_id]


# ------------- Models ----------------------------------------------------
class TransferRequest(BaseModel):
    source_nation_id: str
    target_nation_id: str
    lasso: List[List[float]]  # [[x, y], ...] in normalized 0..1 coords


class TraceRequest(BaseModel):
    type: str  # set_terrain | assign_nation | carve_water | restore_land
    polygon: List[List[float]]  # normalized 0..1 coords
    value: Optional[str] = None  # terrain name or nation id


# ------------- Endpoints -------------------------------------------------
@api_router.get("/")
async def root():
    return {"continent": STATE["continent"], "year": STATE["current_year"]}


@api_router.get("/map/state")
async def get_map_state():
    return dict(**STATE, nation_shapes=_nation_shapes())


@api_router.get("/nation/{nation_id}")
async def get_nation(nation_id: str):
    nation = next((n for n in STATE["nations"] if n["id"] == nation_id), None)
    if not nation:
        raise HTTPException(404, "Nation not found")
    vassals = _vassals_of(nation_id)
    provinces = [p for p in STATE["provinces"] if p["nation_id"] == nation_id]
    settlements = [s for s in STATE["settlements"] if s["nation_id"] == nation_id]
    religion = next((r for r in STATE["religions"] if r["id"] == nation["religion"]), None)
    overlord = None
    if nation.get("overlord"):
        overlord = next((n for n in STATE["nations"] if n["id"] == nation["overlord"]), None)
    return dict(
        nation=nation,
        religion=religion,
        overlord=overlord,
        vassals=vassals,
        provinces=provinces,
        settlements=settlements,
        relations=_relations_for(nation_id),
    )


@api_router.get("/settlement/{settlement_id}")
async def get_settlement(settlement_id: str):
    s = next((s for s in STATE["settlements"] if s["id"] == settlement_id), None)
    if not s:
        raise HTTPException(404, "Settlement not found")
    nation = next((n for n in STATE["nations"] if n["id"] == s["nation_id"]), None)
    province = next((p for p in STATE["provinces"] if p["id"] == s.get("province_id")), None)
    return dict(settlement=s, nation=nation, province=province)


@api_router.post("/map/transfer")
async def transfer(req: TransferRequest):
    if req.source_nation_id == req.target_nation_id:
        raise HTTPException(400, "Source and target must differ")
    src = next((n for n in STATE["nations"] if n["id"] == req.source_nation_id), None)
    tgt = next((n for n in STATE["nations"] if n["id"] == req.target_nation_id), None)
    if not src or not tgt:
        raise HTTPException(404, "Unknown nation id")
    lasso = [(float(x), float(y)) for x, y in req.lasso]
    if len(lasso) < 3:
        raise HTTPException(400, "Lasso needs at least 3 points")

    new_provs, new_setts, area = transfer_territory(
        STATE["provinces"], STATE["settlements"],
        req.source_nation_id, req.target_nation_id, lasso,
    )
    STATE["provinces"] = new_provs
    STATE["settlements"] = new_setts
    _mark_shapes_dirty()

    # Persist snapshot to Mongo (best effort).
    try:
        await db.world_edits.insert_one(dict(
            ts=datetime.now(timezone.utc).isoformat(),
            source=req.source_nation_id, target=req.target_nation_id,
            transferred_area=area,
        ))
    except Exception:
        pass

    return dict(
        ok=True,
        transferred_area=area,
        provinces=STATE["provinces"],
        settlements=STATE["settlements"],
    )


@api_router.post("/map/reset")
async def reset_world(clear_traces: bool = False):
    global TRACES
    STATE["nations"] = copy.deepcopy(SEED_WORLD["nations"])
    STATE["provinces"] = copy.deepcopy(SEED_WORLD["provinces"])
    STATE["settlements"] = copy.deepcopy(SEED_WORLD["settlements"])
    STATE["religions"] = copy.deepcopy(SEED_WORLD["religions"])
    STATE["relations"] = copy.deepcopy(SEED_WORLD["relations"])
    if clear_traces:
        TRACES = []
        _save_traces()
    else:
        _apply_all_traces()  # user corrections survive a map reset
    _mark_shapes_dirty()
    return dict(ok=True, traces_kept=not clear_traces)


# ------------- Trace Mode (manual correction tool) ------------------------
VALID_TRACE_TYPES = {"set_terrain", "assign_nation", "carve_water", "restore_land"}
VALID_TERRAINS = {"plains", "forest", "mountain", "hills", "coast", "desert", "swamp"}


@api_router.get("/trace/overrides")
async def list_traces():
    return dict(traces=TRACES, count=len(TRACES))


@api_router.post("/trace/apply")
async def trace_apply(req: TraceRequest):
    if req.type not in VALID_TRACE_TYPES:
        raise HTTPException(400, f"type must be one of {sorted(VALID_TRACE_TYPES)}")
    if len(req.polygon) < 3:
        raise HTTPException(400, "polygon needs at least 3 points")
    if req.type == "set_terrain":
        if req.value not in VALID_TERRAINS:
            raise HTTPException(400, f"value must be a terrain: {sorted(VALID_TERRAINS)}")
    if req.type in ("assign_nation", "restore_land"):
        if not any(n["id"] == req.value for n in STATE["nations"]):
            raise HTTPException(404, "Unknown nation id in value")

    provs, setts, area = apply_trace(
        STATE["provinces"], STATE["settlements"], req.type, req.polygon, req.value,
    )
    if area <= 0:
        return dict(ok=False, affected_area=0.0,
                    message="Trace did not affect any territory")
    STATE["provinces"] = provs
    STATE["settlements"] = setts
    _mark_shapes_dirty()

    import uuid
    record = dict(
        id=f"t_{uuid.uuid4().hex[:8]}",
        type=req.type,
        polygon=[[float(x), float(y)] for x, y in req.polygon],
        value=req.value,
        ts=datetime.now(timezone.utc).isoformat(),
    )
    TRACES.append(record)
    _save_traces()
    return dict(ok=True, affected_area=area, trace=record,
                provinces=STATE["provinces"], settlements=STATE["settlements"])


@api_router.delete("/trace/overrides/{trace_id}")
async def delete_trace(trace_id: str):
    global TRACES
    before = len(TRACES)
    TRACES = [t for t in TRACES if t["id"] != trace_id]
    if len(TRACES) == before:
        raise HTTPException(404, "Trace not found")
    _save_traces()
    # rebuild from seed + remaining traces
    STATE["provinces"] = copy.deepcopy(SEED_WORLD["provinces"])
    STATE["settlements"] = copy.deepcopy(SEED_WORLD["settlements"])
    _apply_all_traces()
    _mark_shapes_dirty()
    return dict(ok=True, remaining=len(TRACES))


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
