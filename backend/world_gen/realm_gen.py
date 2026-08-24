"""
realm_gen.py — procedural deepening of the feudal world.

- Culture-aware fantasy name generator (deterministic, seeded)
- Vassal generation under the great powers (duchies, marches, counties...)
- Influence stat computation (power dynamics inside a realm)
- Procedural settlement expansion (villages, towns, castles, holy sites)
"""
import colorsys
import random

# ---------------------------------------------------------------------------
# Name generation
# ---------------------------------------------------------------------------
SYLLABLES = {
    "imperial": (["Kas", "Or", "Thren", "Vel", "Dra", "Mar", "Bran", "Stol", "Gard", "Kel"],
                  ["kan", "ther", "mund", "grad", "holt", "var", "brand", "stein", "mark", "wald"],
                  ["", "", "ia", "or", "heim", "burg", "fort", "gate"]),
    "nordic": (["Skal", "Vor", "Hjal", "Thra", "Ulf", "Bryn", "Frey", "Jor", "Kald", "Sven"],
                ["dur", "vik", "gar", "mund", "stad", "fjor", "grim", "vald", "born", "drak"],
                ["", "", "en", "heim", "fell", "ness", "vik"]),
    "desert": (["Qas", "Tal", "Zar", "Nak", "Sah", "Uzir", "Kha", "Mir", "Ras", "Jal"],
                ["im", "qad", "esh", "ara", "uz", "aban", "emir", "ath", "una", "ir"],
                ["", "", "-dar", "-esh", "ah", "oun"]),
    "sylvan": (["Ael", "Syl", "Thae", "Cor", "Ver", "Lir", "Ela", "Myr", "Fen", "Bry"],
                ["var", "wyn", "thal", "iel", "onwe", "aris", "enna", "wick", "loren", "dale"],
                ["", "", "wood", "mere", "glen", "shade"]),
    "dark": (["Vhal", "Mor", "Grim", "Noc", "Dur", "Skor", "Vex", "Bal", "Neth", "Karg"],
              ["gath", "mor", "rax", "thul", "grave", "dreth", "vorn", "khar", "mire", "dun"],
              ["", "", "hold", "spire", "barrow"]),
}
CULTURE_GROUP = {
    "Orthengardian": "imperial", "Solmyri": "imperial", "Andros": "imperial", "Wexili": "imperial",
    "Corregar": "imperial", "Threnwoldic": "imperial", "Drakenmarch": "imperial", "Loxi": "imperial",
    "Volmar": "nordic", "Vaen": "nordic", "Iskali": "nordic", "Isleman": "nordic", "Corsair": "nordic",
    "Karnathi": "desert", "Uzari": "desert", "Sarkathi": "desert", "Nakreshi": "desert", "Zoskan": "desert",
    "Karthi": "desert", "Ghurric": "desert", "Mokhuri": "desert",
    "Sylvan": "sylvan", "Cerelithi": "sylvan", "Elmi": "sylvan", "Thelmi": "sylvan", "Fenlander": "sylvan",
    "Merevaulti": "sylvan", "Brackeni": "sylvan",
    "Vhalari": "dark", "Grey": "dark", "Wyrmbound": "dark", "Grumnari": "dark",
}


def make_name(rng, culture, used=None):
    group = CULTURE_GROUP.get(culture, "imperial")
    starts, mids, ends = SYLLABLES[group]
    for _ in range(30):
        name = rng.choice(starts) + rng.choice(mids) + rng.choice(ends)
        if used is None or name not in used:
            if used is not None:
                used.add(name)
            return name
    return name + str(rng.randint(2, 9))


RULER_FIRST = ["Aldric", "Berthold", "Cassia", "Doran", "Elsbeth", "Fyodor", "Gwynne", "Hakon",
               "Isolde", "Jorund", "Katrin", "Lothar", "Maelys", "Njall", "Oswin", "Petra",
               "Quintus", "Ragna", "Sableth", "Tormund", "Ulrika", "Vestan", "Wilhelmina", "Yrsa", "Zavian"]

VASSAL_TIERS = {
    "empire": [("duchy", "Duchy of {}", "Duke", 30), ("margraviate", "Margraviate of {}", "Margrave", 20),
               ("county", "County of {}", "Count", 25), ("prince_bishopric", "Prince-Bishopric of {}", "Prince-Bishop", 10),
               ("barony", "Barony of {}", "Baron", 15)],
    "kingdom": [("duchy", "Duchy of {}", "Duke", 35), ("county", "County of {}", "Count", 40),
                ("barony", "Barony of {}", "Baron", 25)],
    "sultanate": [("emirate", "Emirate of {}", "Emir", 50), ("beylik", "Beylik of {}", "Bey", 30),
                  ("waziriate", "Waziriate of {}", "Wazir", 20)],
    "theocracy": [("prelacy", "Prelacy of {}", "Prelate", 50), ("templar_march", "Templar-March of {}", "Grand Templar", 50)],
    "confederacy": [("clan_union", "Clanhold of {}", "Clan-Chief", 60), ("jarldom", "Jarldom of {}", "Jarl", 40)],
}

MOTTOS = ["Iron Keeps Faith", "By Root and Crown", "The Watch Endures", "Salt and Steel",
          "No Oath Broken", "From Ash, Order", "The River Remembers", "Stone Outlasts Storm",
          "Loyal Unto Ruin", "The Border Holds", "First in the Vanguard", "Beneath One Banner"]

VASSAL_LORE = [
    "Sworn to {overlord} after the Treaty of the {place} Fords, its lords still mint their own coin — a privilege bought in blood.",
    "Raised from a frontier garrison to a hereditary seat, {place} guards the marches and grumbles at every levy demanded by {overlord}.",
    "The house of {place} claims older blood than its overlord, and its banners fly a half-inch higher than custom allows.",
    "{place} was granted its charter for service in the Winter War; its knights remain the finest heavy cavalry sworn to {overlord}.",
    "A quiet, prosperous fief whose tolls on the old trade road fill the coffers of {overlord} — and, quietly, its own.",
    "Twice {place} has risen in revolt, and twice been pardoned; its loyalty is a coin that must be re-purchased each generation.",
]


def shade_color(hex_color, rng):
    """Produce a lighter/darker/hue-shifted shade of the overlord colour."""
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255
    hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
    hh = (hh + rng.uniform(-0.045, 0.045)) % 1.0
    ll = min(0.72, max(0.22, ll + rng.uniform(-0.14, 0.18)))
    ss = min(0.9, max(0.15, ss + rng.uniform(-0.12, 0.08)))
    r2, g2, b2 = colorsys.hls_to_rgb(hh, ll, ss)
    return "#{:02x}{:02x}{:02x}".format(int(r2 * 255), int(g2 * 255), int(b2 * 255))


def gen_vassals(nations, rng=None):
    """Generate vassals under every major power. Returns new nation dicts.

    Realms are meant to be MAJORITY-vassal, so we create a generous number of
    vassals per overlord and spread their seats across the overlord's anchors so
    they cover the whole realm (the generator's majority-vassal pass then hands
    most overlord land to the nearest vassal)."""
    import math
    rng = rng or random.Random(892)
    used_names = set()
    by_overlord = {}
    for n in nations:
        if n.get("overlord"):
            by_overlord.setdefault(n["overlord"], []).append(n)

    targets = {
        "empire": 11, "kingdom": 8, "sultanate": 8, "theocracy": 6, "confederacy": 6,
        "khanate": 6, "free_kingdom": 5, "grand_duchy": 5, "merchant_republic": 5,
        "tribal_kingdom": 5, "federation": 5, "duchy": 4, "principality": 4,
    }
    new_nations = []
    for n in nations:
        if n.get("overlord") or n["tier"] not in targets:
            continue
        want = targets[n["tier"]]
        have = len(by_overlord.get(n["id"], []))
        pool = VASSAL_TIERS.get(n["tier"], VASSAL_TIERS["kingdom"])
        anchors = n["seed_points"]
        for k in range(max(0, want - have)):
            tier, pattern, title, _w = rng.choices(pool, weights=[p[3] for p in pool])[0]
            place = make_name(rng, n["culture"], used_names)
            # Spread vassals across ALL the overlord's anchors (round-robin) so
            # they fill the whole realm rather than clustering at one point.
            ax, ay = anchors[k % len(anchors)]
            ang = rng.uniform(0, 6.28318)
            dist = rng.uniform(0.02, 0.055)
            sx = min(0.99, max(0.01, ax + dist * rng.uniform(0.5, 1.0) * math.cos(ang)))
            sy = min(0.95, max(0.01, ay + dist * rng.uniform(0.5, 1.0) * math.sin(ang)))
            # A second seed point gives each vassal a larger, more natural
            # territory footprint.
            ang2 = ang + rng.uniform(1.8, 4.5)
            d2 = rng.uniform(0.018, 0.042)
            sx2 = min(0.99, max(0.01, sx + d2 * math.cos(ang2)))
            sy2 = min(0.95, max(0.01, sy + d2 * math.sin(ang2)))
            army = rng.randint(12, 55)
            econ = rng.randint(15, 60)
            seat_name = make_name(rng, n["culture"], used_names)
            new_nations.append(dict(
                id=f"v_{place.lower()}_{rng.randint(100,999)}",
                name=pattern.format(place),
                tier=tier,
                color=shade_color(n["color"], rng),
                overlord=n["id"],
                religion=n["religion"] if rng.random() < 0.85 else n["religion"],
                ruler=f"{title} {rng.choice(RULER_FIRST)} of {place}",
                ruler_title=title,
                culture=n["culture"],
                motto=rng.choice(MOTTOS),
                founded=f"3E {rng.randint(120, 860)}",
                army=army,
                economy=econ,
                description=f"A {tier.replace('_', ' ')} sworn to {n['name']}.",
                lore=rng.choice(VASSAL_LORE).format(overlord=n["name"], place=place),
                seed_points=[(sx, sy), (sx2, sy2)],
                settlements=[dict(
                    name=seat_name, type="city", x=sx, y=sy,
                    description=f"Seat of the {tier.replace('_', ' ')} of {place}.",
                    lore=f"{seat_name} keeps the charter-scrolls of {place} in a vaulted hall; "
                         f"its market bell rings thrice for trade and once for war.",
                )],
            ))
    return new_nations


def compute_influence(nation, area, prov_count, settlement_count):
    """0-100 influence score: martial + wealth + land + infrastructure."""
    score = (
        0.35 * nation.get("army", 20)
        + 0.30 * nation.get("economy", 20)
        + min(25.0, area * 2600.0)
        + min(10.0, settlement_count * 1.5)
    )
    return int(max(3, min(98, round(score))))


# ---------------------------------------------------------------------------
# Procedural settlements
# ---------------------------------------------------------------------------
SETTLE_DESC = {
    "village": ["A cluster of turf-roofed crofts around a mossy well.",
                "Sheep-folds, a mill, and one stubborn inn.",
                "Charcoal burners and beekeepers pay their tithe here.",
                "A palisaded hamlet living off the land."],
    "town": ["A market town of timber galleries and a toll bridge.",
             "Guild banners hang over its cramped, busy lanes.",
             "Its fair is famous for wool, salt and gossip.",
             "A river town of tanners, coopers and boatwrights."],
    "castle": ["A stern keep watching the border roads.",
               "Star-walled fortress, never taken by storm.",
               "A crag-top hold with beacons kept dry.",
               "Garrison seat of the local levy."],
    "holy_site": ["A shrine ringed by pilgrim stones.",
                  "An old sanctum tended by three silent keepers.",
                  "Relic-hall drawing pilgrims each Bloom-tide."],
    "port": ["A harbour of tarred piers and fish-smoke.",
             "Sheltered anchorage with a chain-tower.",
             "A trade quay where three currents meet."],
}


def gen_settlements(rng, nation, geom, count, used_names, sample_inside):
    """Generate procedural minor settlements inside nation territory."""
    out = []
    weights = [("village", 0.48), ("town", 0.26), ("castle", 0.14), ("holy_site", 0.12)]
    for _ in range(count):
        pt = sample_inside(geom, rng)
        if pt is None:
            continue
        r = rng.random()
        acc = 0
        stype = "village"
        for t, w in weights:
            acc += w
            if r <= acc:
                stype = t
                break
        name = make_name(rng, nation["culture"], used_names)
        out.append(dict(
            name=name, type=stype, x=round(pt[0], 5), y=round(pt[1], 5),
            description=rng.choice(SETTLE_DESC[stype]),
            lore=f"{name} — {rng.choice(SETTLE_DESC[stype])}",
        ))
    return out
