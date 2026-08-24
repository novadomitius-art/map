"""
Kelvaros — Hand-authored world catalog for the Political Map Game.
~54 nations, 8 religions, 5 major powers + 16 vassals + 33 independents.
Fresh medieval-fantasy names (no real-world derivations, no clichés).

All coordinates are normalized 0..1  (x right, y down)  against base_map.webp.
Seed points define province territory (Voronoi cells clipped to the land mask).
Each nation has 1-4 provinces (seed points), 3-8 settlements, and hand-authored lore.
"""

CONTINENT_NAME = "Kelvaros"
CURRENT_YEAR = "3E 892"          # Third Reckoning
CONTINENT_LORE = (
    "Kelvaros — the Bruised Realm — is a continent of jagged coasts, ancient mountain "
    "belts and a great inland Rift Sea. For eight centuries after the Sundering of the "
    "Old Kings, its peoples have fractured and re-forged themselves into a mosaic of "
    "empires, marches, tribal khanates and hidden fanes. Five great powers hold sway; "
    "a hundred lesser lords chafe against them."
)

# ------------------------------- RELIGIONS ---------------------------------
RELIGIONS = [
    dict(id="ord_flame", name="Ordinion of the Twelve Flames",
         color="#e9c46a",
         deity="The Twelve Saint-Flames of Ordis",
         description="Cathedral faith of the civilised realms.",
         lore=("Founded by the martyr-prophet Ordis at the Kindling of Solmyr in 1E 214, "
               "the Ordinion venerates twelve flames of virtue — Mercy, Iron, Harvest, "
               "Song, Vigil, Toil, Bloom, Judgement, Silence, Sail, Hearth and Ash. Its "
               "seat is the Basilica of Twelvefold Light in Solmyr. Priests are marked "
               "at ordination with a small brand on the palm.")),
    dict(id="karnathi_sun", name="Karnathi Sun-Doctrine",
         color="#f4a261",
         deity="Ka-Namar, the Unblinking",
         description="Sun-monotheism of the great desert.",
         lore=("The Karnathi hold that Ka-Namar, the Unblinking, is the sole eye of "
               "creation and that shadow is heresy given form. Their calendar is measured "
               "in Blazes, and their temples are stepped ziggurats of pale sandstone. "
               "The Grand Muezzin-of-Fires in Tal-Qadis holds spiritual primacy.")),
    dict(id="veyral", name="Veyral Path",
         color="#2a9d8f",
         deity="The Green Convocation",
         description="Druidic faith of the deep forests.",
         lore=("The Veyral teach that the Wilds and the Kin are two halves of one breath. "
               "There is no clergy — only the Green Convocation, an assembly of "
               "grove-keepers who meet each Bloom-tide beneath the Mother-Yew of "
               "Aelvarim. Practitioners bear a leaf-scar across the throat.")),
    dict(id="stonefaith", name="Old Stone Faith",
         color="#8d99ae",
         deity="The Ancestor-Stones",
         description="Oldest religion; mountain and northern pagan.",
         lore=("Older than the Twelve Flames by a thousand winters, the Old Stone Faith "
               "worships the frost-carved standing stones said to hold the voices of "
               "the first mortals. Its rites are austere: circle-walking at dawn, "
               "salt-libations at dusk, and the Long Watch before winter.")),
    dict(id="deep_fathom", name="Cult of the Deep Fathom",
         color="#264653",
         deity="The Drowned King",
         description="Seafarers' faith; the Drowned King in the trench.",
         lore=("Sailors, corsairs and coastal reavers swear by the Drowned King, a "
               "chained titan said to sleep in a lightless trench beneath the Rift Sea. "
               "The devout are tattooed with fathom-marks and, upon death, are weighted "
               "with iron and given to the waters.")),
    dict(id="ashen_cov", name="Ashen Covenant",
         color="#4a4e69",
         deity="The Grey Saint of Ash",
         description="Heretical splinter of the Ordinion; embraces suffering.",
         lore=("Condemned as heretical by the Basilica in 3E 411, the Ashen Covenant "
               "holds that the Twelve Flames burn wrongly — that only ash remains after "
               "all fire, and thus ash is the truest sacrament. Its adherents wear grey "
               "and rub cinder into their brows before speech.")),
    dict(id="dhrenic", name="Dhrenic Ancestrism",
         color="#a68a64",
         deity="The Twelve Grandfathers",
         description="Tribal ancestor worship of the steppe and northern wildlands.",
         lore=("The steppe-clans, fen-lords and northern barbarians revere the Twelve "
               "Grandfathers — mythic founding chieftains whose spirits are said to ride "
               "the wind. Each moot begins with the Naming, a recital of ancestry going "
               "back at least three generations.")),
    dict(id="wyrm_creed", name="Wyrmbound Creed",
         color="#9b2226",
         deity="Ozarel, the Rust-Scaled",
         description="Dragon worship of the Drakenspur peaks.",
         lore=("A cult that once burnt whole villages for tribute to Ozarel, the "
               "Rust-Scaled dragon said to slumber beneath the tallest Drakenspur peak. "
               "Since the Purging of 3E 702 the creed has retreated to hidden shrines, "
               "but its adherents still bind their forearms in copper wire in Ozarel's "
               "honour."))
]


# ------------------------------- HELPERS -----------------------------------
def _mk_settlement(name, stype, x, y, desc, lore=""):
    return dict(name=name, type=stype, x=x, y=y, description=desc, lore=lore or desc)


# ------------------------------- NATIONS -----------------------------------
# Every nation entry contains:
#   id, name, tier, color, overlord (or None), religion, ruler, ruler_title, culture,
#   motto, founded ("XE YYY"), description, lore (multi-para), army, economy,
#   seed_points (2-4 xy tuples inside its territory — provinces build from these),
#   settlements (list of settlement dicts).
#
# The generator will run Voronoi on ALL seed points across ALL nations, clip cells
# to the land mask, and assign each cell to the nation that owns that seed point.
# Nation-color polygons emerge naturally from unioning the cells.

NATIONS = [
    # =============== MAJOR POWERS (5) ===============
    dict(
        id="orthengard",
        name="Empire of Orthengard",
        tier="empire",
        color="#8c2f39",
        overlord=None,
        religion="ord_flame",
        ruler="Emperor Aureth IV Vareth-Kaskan",
        ruler_title="Emperor of the Twelvefold Throne",
        culture="Orthengardian",
        motto="From the Iron Spine, Iron Rule",
        founded="1E 486",
        army=98, economy=92,
        description="The dominant power of eastern Kelvaros — an iron-forged empire seated on the Iron Spine mountains.",
        lore=(
            "Orthengard rose from the ashes of the Third Sundering when the warlord "
            "Kaskan the Unbroken hammered nine feuding houses into a single crown at the "
            "Council of Ash-Iron in 1E 486. The empire's spine — literally — is the "
            "great Iron Spine Range that shields it from northern raiders; its lifeblood "
            "is the sacred river Kelvarne, whose waters are said to have been blessed by "
            "the Twelve Flames themselves.\n\n"
            "For four centuries the Twelvefold Throne has expanded south and west, "
            "swallowing lesser kingdoms into vassalage. Its army — the Legions of "
            "Ash-Iron — is drawn from a hereditary caste of iron-branded soldiers who "
            "may not marry outside their legion. The current emperor, Aureth IV, is a "
            "cautious scholar-king who has spent his reign consolidating the marches "
            "and quietly starving the heretical Ashen Covenant of its patrons.\n\n"
            "Orthengard's rivalries are old: it has fought seven declared wars with the "
            "Sultanate of Qadi-Sharr over the pass-fortresses of the Iron Spine, and it "
            "regards the Kingdom of Volmarr with the wary respect one gives an old wolf."
        ),
        seed_points=[(0.72, 0.10), (0.80, 0.16), (0.88, 0.22), (0.86, 0.32), (0.76, 0.28),
                     (0.92, 0.14), (0.68, 0.18)],
        settlements=[
            _mk_settlement("Kaskangrad", "capital", 0.80, 0.18,
                "The Imperial Seat. City of nine iron-gated tiers rising against the Iron Spine.",
                "Kaskangrad was raised on the tomb of Kaskan the Unbroken in 1E 492. Its nine tiers "
                "correspond to the nine houses of the Founding, and each tier is walled in a different "
                "shade of blackened iron. The Twelvefold Basilica of the Imperial Rite crowns the topmost tier."),
            _mk_settlement("Vareth-on-Kelvarne", "city", 0.72, 0.20,
                "River-city of the ruling Vareth cadet branch. Famous for its bell-foundries."),
            _mk_settlement("Ostbrach", "city", 0.88, 0.28,
                "Frontier city guarding the eastern coast; largest port in the empire."),
            _mk_settlement("Fort Kaskir", "castle", 0.86, 0.14,
                "The Iron Bulwark. Never taken by force in four centuries."),
            _mk_settlement("Erdenholm", "town", 0.76, 0.10,
                "Foundry town supplying the Legions of Ash-Iron."),
            _mk_settlement("Marbeck", "town", 0.92, 0.20,
                "Coastal town of fishermen and iron-mongers."),
            _mk_settlement("Grimling", "village", 0.68, 0.14,
                "Mountain village clinging to the western slopes."),
            _mk_settlement("Ossen", "castle", 0.94, 0.10,
                "Watch-fort of the Northern March."),
            _mk_settlement("Port Aureth", "major_port", 0.94, 0.26,
                "The empire's grand naval harbour; twelve bell-towers ring dawn."),
        ],
    ),
    dict(
        id="volmarr",
        name="Kingdom of Volmarr",
        tier="kingdom",
        color="#3d5a80",
        overlord=None,
        religion="stonefaith",
        ruler="King Halgar the Silver-Beard",
        ruler_title="High King of the Fjord-Reach",
        culture="Volmar",
        motto="What the Cold Made, the Cold Keeps",
        founded="2E 018",
        army=74, economy=68,
        description="Coastal fjord kingdom of long-hulled ships and Ancestor-Stone worship.",
        lore=(
            "Volmarr was forged when the sea-jarl Halgar the Elder united the fjord "
            "clans in 2E 018 by the simple expedient of sinking every rival ship in the "
            "Fjord Reach. His descendants — the House of Halgarim — have ruled for eight "
            "hundred years with the aid of a hereditary council of ship-jarls.\n\n"
            "The Volmar are the last great practitioners of the Old Stone Faith; their "
            "kings are crowned atop the Ancestor-Stone of Grimhal, where each new "
            "monarch stands vigil for a full winter night. They are seafarers first, "
            "and their long-hulled skorne-ships dominate the northern trade lanes.\n\n"
            "Halgar the Silver-Beard, the current king, is now in his eighty-first year "
            "and has no acknowledged heir. Three of his ship-jarls quietly circle the "
            "throne like gulls; a succession war is expected within the decade."
        ),
        seed_points=[(0.42, 0.05), (0.36, 0.10), (0.48, 0.06), (0.44, 0.12), (0.30, 0.14),
                     (0.24, 0.14)],
        settlements=[
            _mk_settlement("Halgarim", "capital", 0.42, 0.08,
                "Ancient capital raised on the Ancestor-Stone of Grimhal.",
                "Halgarim's central plaza is the Ancestor-Stone itself — a twenty-foot menhir "
                "carved with the names of every High King back to Halgar the Elder. The stone is "
                "said to grow warm when a false claimant lays hands upon it."),
            _mk_settlement("Skorne-Anchor", "major_port", 0.30, 0.14,
                "The mother-harbour of the Volmar longfleet; a forest of black masts."),
            _mk_settlement("Ravnholt", "city", 0.48, 0.10,
                "City of the ravens; seat of the House of Ravnhal."),
            _mk_settlement("Weissfjord", "port", 0.24, 0.16,
                "Ice-locked port that ships silver from the fjord-mines."),
            _mk_settlement("Kaergrim", "castle", 0.44, 0.05,
                "Cliff-fortress overlooking the Northern Reanic Ocean."),
            _mk_settlement("Osfjard", "village", 0.36, 0.06,
                "Fjord-side fishing village famed for its smoked kelp."),
        ],
    ),
    dict(
        id="qadi_sharr",
        name="Sultanate of Qadi-Sharr",
        tier="sultanate",
        color="#e9b872",
        overlord=None,
        religion="karnathi_sun",
        ruler="Sultan Selim-Ka the Fourth",
        ruler_title="Muezzin-Sovereign of the Sun-Throne",
        culture="Karnathi",
        motto="The Sun Does Not Kneel",
        founded="2E 341",
        army=82, economy=88,
        description="Sun-worshipping sultanate ruling the Great Kelvaran Desert.",
        lore=(
            "The Sultanate of Qadi-Sharr rose in 2E 341 when the desert-prophet "
            "Selim-Ka the First united the twelve nomadic wazir-clans under a single "
            "green banner. The sultanate is technically an elective monarchy: upon each "
            "sultan's death the wazir-council convenes at the Ziggurat of Tal-Qadis to "
            "choose from the eligible male-line descendants. In practice the Selim-Ka "
            "line has held the throne unbroken for four centuries.\n\n"
            "Qadi-Sharr is wealthy beyond its arid reputation — its caravans control the "
            "Cinnamon Road that binds the eastern coast to the western fjords, and its "
            "sun-glass artisans are considered the finest on the continent. Its army "
            "combines heavy sun-glass cavalry with the feared Muezzin-Guards, warrior-"
            "priests who fight blindfold against the shadow.\n\n"
            "Selim-Ka IV is famously patient: he has spent his reign quietly strangling "
            "Orthengardian trade routes rather than open war. Analysts in Solmyr believe "
            "he waits only for Aureth IV to falter before striking north."
        ),
        seed_points=[(0.48, 0.42), (0.54, 0.44), (0.58, 0.40), (0.52, 0.48), (0.44, 0.44),
                     (0.60, 0.46), (0.50, 0.38)],
        settlements=[
            _mk_settlement("Tal-Qadis", "capital", 0.52, 0.43,
                "The White Ziggurat. Sun-throne of the Muezzin-Sovereign.",
                "Tal-Qadis is the only stepped ziggurat in Kelvaros — seven tiers of pale sandstone "
                "raised in 2E 342, one tier for each Blaze of the sacred calendar. Its summit holds "
                "the Sun-Throne, a chair of polished obsidian into which twelve mirrors are set."),
            _mk_settlement("Ez-Kahar", "city", 0.58, 0.40,
                "Trade-city; hub of the Cinnamon Road."),
            _mk_settlement("Tamûr", "city", 0.44, 0.44,
                "Oasis-city ringed with date-palms."),
            _mk_settlement("Selkanth", "city", 0.60, 0.48,
                "Southern city guarding the desert's fringe."),
            _mk_settlement("Fort Al-Vazir", "castle", 0.48, 0.38,
                "Desert-fort at the western pass."),
            _mk_settlement("Halaqim Well", "town", 0.50, 0.48,
                "Caravan-well and last watering-place before the Ashen Steppe."),
        ],
    ),
    dict(
        id="sylvan_reach",
        name="Confederacy of the Sylvan Reach",
        tier="confederacy",
        color="#436436",
        overlord=None,
        religion="veyral",
        ruler="Speaker-in-Green Meilith Aelvarim",
        ruler_title="Speaker of the Green Convocation",
        culture="Sylvan",
        motto="The Wood Remembers",
        founded="2E 604",
        army=64, economy=52,
        description="Loose confederacy of Emberpine forest realms bound by the Veyral Path.",
        lore=(
            "The Sylvan Reach is less a state than a covenant: in 2E 604 the four great "
            "forest-lords of the Emberpine met beneath the Mother-Yew of Aelvarim and "
            "swore the Bough-Oath — that they would defend the Deepwood together and "
            "otherwise leave one another alone. That oath has held, imperfectly, ever since.\n\n"
            "The Reach is ruled in council by the Speaker-in-Green, a lifetime post "
            "chosen by acclamation at each Bloom-tide. The current Speaker, Meilith "
            "Aelvarim, is only the fourth woman to hold the role and is famed for having "
            "single-handedly negotiated the peace of the Charred Cantons in 3E 878.\n\n"
            "The Reach's armies are small but the Deepwood is its greatest weapon: no "
            "invading force in six hundred years has taken more than the woodland's "
            "shallow edge. Its rivalry with the Sultanate of Qadi-Sharr is old and "
            "cold — the desert-folk consider the Reach a haven for shadow-heretics."
        ),
        seed_points=[(0.10, 0.78), (0.14, 0.72), (0.06, 0.82), (0.16, 0.86), (0.10, 0.88),
                     (0.20, 0.76)],
        settlements=[
            _mk_settlement("Aelvarim", "capital", 0.10, 0.80,
                "Grove-capital beneath the Mother-Yew.",
                "Aelvarim has no walls — the Emberpine itself is its defence. Its Grove-Council "
                "meets in a natural amphitheatre of interlaced yews said to be older than the "
                "Ordinion. The Mother-Yew's roots reach, by legend, to the very heart of Kelvaros."),
            _mk_settlement("Hollowreach", "city", 0.14, 0.74,
                "River-city on the Emberpine's northern edge."),
            _mk_settlement("Thornhaven", "city", 0.16, 0.86,
                "Fortified enclave of the Wardens of Thorn."),
            _mk_settlement("Green-Warden Keep", "castle", 0.06, 0.82,
                "Ancient bough-fortress; seat of the standing army."),
            _mk_settlement("Silverbough", "town", 0.20, 0.78,
                "Silver-birch grove home to the Reach's only smithy of note."),
            _mk_settlement("Mossgate", "village", 0.10, 0.88,
                "Southern village at the edge of the Whispering Fens."),
        ],
    ),
    dict(
        id="solmyr",
        name="Theocracy of Solmyr",
        tier="theocracy",
        color="#f2e8cf",
        overlord=None,
        religion="ord_flame",
        ruler="Ordinat Miriach the Fourteenth",
        ruler_title="Ordinat of the Twelve Flames",
        culture="Solmyri",
        motto="Twelve Flames, One Light",
        founded="1E 214",
        army=70, economy=76,
        description="Theocratic seat of the Ordinion of the Twelve Flames.",
        lore=(
            "Solmyr is the mother-realm of the Ordinion of the Twelve Flames, founded in "
            "1E 214 when the martyr-prophet Ordis kindled the First Flame in the ruins of "
            "an older city whose name is not spoken. It is ruled by the Ordinat — a "
            "lifetime religious sovereign chosen by the Conclave of Twelve.\n\n"
            "Solmyr is not the largest realm, but it is spiritually pre-eminent: every "
            "monarch in Kelvaros save the Karnathi and the Volmar has been crowned "
            "with the blessing of the Basilica. The Templar-March of Kaldros, its "
            "sworn militant order, has intervened in twenty-eight recorded wars.\n\n"
            "Ordinat Miriach XIV is a former Templar of Kaldros — a warrior turned "
            "cleric — and his reign has hardened the Basilica against the Ashen "
            "Covenant. Whispers say he plans to declare a Twelfth Kindling, a rite that "
            "has been performed only twice in eight hundred years, both times "
            "immediately preceding continental war."
        ),
        seed_points=[(0.60, 0.66), (0.66, 0.62), (0.62, 0.72), (0.56, 0.68), (0.68, 0.68),
                     (0.72, 0.64)],
        settlements=[
            _mk_settlement("Solmyr", "capital", 0.62, 0.66,
                "The Kindled City. Seat of the Basilica of Twelvefold Light.",
                "Solmyr was founded upon the exact spot where the martyr-prophet Ordis kindled the "
                "First Flame in 1E 214. The Basilica of Twelvefold Light stands at its centre — "
                "twelve concentric bronze halls beneath a single crystal dome, and the Perpetual "
                "Flame at the heart has burnt without interruption for six hundred and seventy-eight years."),
            _mk_settlement("Ostium", "city", 0.60, 0.72,
                "Southern city-port; seat of the Prelacy."),
            _mk_settlement("Kaldros", "city", 0.68, 0.62,
                "Militant seat of the Templar-March."),
            _mk_settlement("Belkharim", "city", 0.72, 0.66,
                "Eastern city-fortress overlooking the Ashen Steppe."),
            _mk_settlement("Twelve-Flame Keep", "castle", 0.56, 0.68,
                "The Ordinat's personal fortress; twelve bronze towers ring an inner keep."),
            _mk_settlement("Harvest-Hall", "town", 0.66, 0.70,
                "Cathedral-town of the Bloom-flame; famous grain-tithes."),
            _mk_settlement("Port Ordis", "major_port", 0.58, 0.74,
                "The Ordinat's harbour; every ship blessed at the pierhead."),
        ],
    ),

    # =============== VASSALS OF ORTHENGARD (4) ===============
    dict(
        id="kern_vareth", name="Duchy of Kern-Vareth", tier="duchy",
        color="#b5545c", overlord="orthengard", religion="ord_flame",
        ruler="Duke Aldrin Vareth-Kern", ruler_title="Duke of Kern-Vareth",
        culture="Orthengardian", motto="Iron Beneath the Iron", founded="2E 118",
        army=44, economy=48,
        description="Chief vassal-duchy of Orthengard; ancestral seat of the Vareth cadet lineage.",
        lore=("Kern-Vareth was granted to the second son of Kaskan the Unbroken in 2E 118 "
              "and has remained the empire's most loyal vassal ever since. Its duke sits "
              "at the emperor's left hand at every Council of Ash-Iron. The current duke, "
              "Aldrin, is a childhood friend of Emperor Aureth IV and is expected to be "
              "named Regent should the ailing emperor die before naming an heir."),
        seed_points=[(0.66, 0.24), (0.70, 0.28), (0.62, 0.28)],
        settlements=[
            _mk_settlement("Kern-Vareth", "capital", 0.66, 0.26, "Foundry-capital of black iron."),
            _mk_settlement("Ash-Vareth", "town", 0.70, 0.30, "Ash-crossing town on the Kelvarne."),
            _mk_settlement("Grimhold", "castle", 0.62, 0.28, "Guarding the Vareth Pass."),
        ],
    ),
    dict(
        id="ostenmark", name="Margraviate of Ostenmark", tier="margraviate",
        color="#c17c74", overlord="orthengard", religion="ord_flame",
        ruler="Margravine Ilsith Kaskan-Ostmar", ruler_title="Margravine of Ostenmark",
        culture="Orthengardian", motto="The Border Holds", founded="2E 245",
        army=52, economy=40,
        description="Frontier march guarding Orthengard's northern approaches.",
        lore=("The Margraviate of Ostenmark was carved from conquered barbarian lands in "
              "2E 245 as a permanent frontier bulwark. Its rulers hold the hereditary "
              "right to raise levies without imperial writ — a privilege granted so they "
              "may repel raids from the Barbarian Confederacy of Ghurr, whose horsemen "
              "still test the border every third summer."),
        seed_points=[(0.58, 0.10), (0.62, 0.06), (0.54, 0.14)],
        settlements=[
            _mk_settlement("Ostenmark", "capital", 0.60, 0.10, "The March-capital; permanent war-camp turned city."),
            _mk_settlement("Fort Kaskan", "castle", 0.54, 0.14, "Named for the empire's founder; scarred by twenty sieges."),
            _mk_settlement("Rimewatch", "town", 0.62, 0.06, "Northernmost town of the empire."),
        ],
    ),
    dict(
        id="threnhold", name="Principality of Threnhold", tier="principality",
        color="#9d4d55", overlord="orthengard", religion="ord_flame",
        ruler="Prince Halveric Threnhold-Vareth", ruler_title="Prince of Threnhold",
        culture="Orthengardian", motto="Old Blood, Old Faith", founded="1E 891",
        army=32, economy=52,
        description="Old princely house predating the empire; retained autonomy as vassal.",
        lore=("Threnhold's princes trace their line to before the Third Sundering. When "
              "Kaskan the Unbroken forged the empire, the then-Prince Halvarim knelt "
              "voluntarily in exchange for perpetual princely dignity and exemption from "
              "the iron-branding of the legions. The bargain has held for four centuries "
              "and is renewed at each imperial coronation."),
        seed_points=[(0.78, 0.32), (0.82, 0.36), (0.74, 0.34)],
        settlements=[
            _mk_settlement("Threnhold", "capital", 0.78, 0.34, "Old princely city of amber-tiled roofs."),
            _mk_settlement("Halvarim's Keep", "castle", 0.82, 0.36, "The original princely seat."),
            _mk_settlement("Amberford", "town", 0.74, 0.32, "River-crossing town; famed amber trade."),
        ],
    ),
    dict(
        id="iskal", name="Free City of Iskal", tier="free_city",
        color="#d4a5a5", overlord="orthengard", religion="ord_flame",
        ruler="Doge Marek Iskalim", ruler_title="Doge of Iskal",
        culture="Iskali", motto="Coin Above Crown", founded="2E 512",
        army=18, economy=88,
        description="Merchant-Doge city holding autonomous vassalage under Orthengard.",
        lore=("Iskal is a coastal merchant-oligarchy whose charter allows it to rule "
              "itself in exchange for a substantial annual tribute and the right to "
              "impress its fleet in imperial war. Its Doges are elected for six years by "
              "the Council of Guilds; the current Doge, Marek Iskalim, is a fourth-"
              "generation banker whose family holds forty percent of imperial debt."),
        seed_points=[(0.90, 0.36), (0.92, 0.32)],
        settlements=[
            _mk_settlement("Iskal", "capital", 0.91, 0.34, "The Doge-city. Twin lighthouses of green flame guard the harbour.",
                "Iskal's harbour is guarded by twin lighthouses that burn with green sea-flame — "
                "an alchemical trick jealously guarded by the Guild of Flames. The Doge's palace "
                "sits on twelve reclaimed islets connected by silver-railed bridges."),
            _mk_settlement("Little-Iskal", "port", 0.94, 0.32, "Auxiliary port for the grain fleet."),
        ],
    ),

    # =============== VASSALS OF VOLMARR (3) ===============
    dict(
        id="skorne", name="Jarldom of Skorne", tier="jarldom",
        color="#4f6d8c", overlord="volmarr", religion="stonefaith",
        ruler="Jarl Ragnhal Skorn-Halgarim", ruler_title="Jarl of Skorne",
        culture="Volmar", motto="Long Keels, Long Winters", founded="2E 018",
        army=32, economy=42,
        description="Ship-jarldom holding the harbour of Skorne-Anchor.",
        lore=("Skorne holds the mother-harbour of the Volmar longfleet — every warship "
              "of the kingdom is launched from its slipways. Its jarl commands the "
              "hereditary Admiralty of the Reach. Ragnhal is one of the three "
              "ship-jarls circling Halgar the Silver-Beard's succession."),
        seed_points=[(0.30, 0.10), (0.34, 0.14)],
        settlements=[
            _mk_settlement("Skorne-Anchor", "capital", 0.30, 0.14, "Mother-harbour of the Volmar longfleet."),
            _mk_settlement("Skorne-Keep", "castle", 0.34, 0.10, "Cliff-keep of the Skorn line."),
        ],
    ),
    dict(
        id="ravnhal", name="Duchy of Ravnhal", tier="duchy",
        color="#5a7591", overlord="volmarr", religion="stonefaith",
        ruler="Duchess Ynga Ravnhal", ruler_title="Duchess of Ravnhal",
        culture="Volmar", motto="The Ravens Return", founded="2E 218",
        army=28, economy=38,
        description="Raven-banner duchy of the eastern fjords.",
        lore=("Ravnhal's house-sign is the raven, and it maintains a hereditary rookery "
              "at Ravnholt whose birds are trained to carry messages across the whole "
              "kingdom. Duchess Ynga is Halgar's own niece and one of three succession claimants."),
        seed_points=[(0.48, 0.06), (0.50, 0.12)],
        settlements=[
            _mk_settlement("Ravnholt", "capital", 0.48, 0.10, "Raven-city; hereditary rookery of the ducal messengers."),
            _mk_settlement("Osrahal", "town", 0.50, 0.06, "Fjord town of shipwrights."),
        ],
    ),
    dict(
        id="weissfjord", name="Barony of Weissfjord", tier="barony",
        color="#6685a1", overlord="volmarr", religion="stonefaith",
        ruler="Baron Erik Weissim", ruler_title="Baron of Weissfjord",
        culture="Volmar", motto="Silver from Ice", founded="2E 344",
        army=18, economy=54,
        description="Ice-locked silver-mining barony of the far western fjords.",
        lore=("Weissfjord's silver mines — carved directly into the fjord walls — supply "
              "the Volmar treasury. The barony is ice-locked six months of every year, "
              "but its wealth per capita is the highest in the kingdom."),
        seed_points=[(0.24, 0.16), (0.20, 0.20)],
        settlements=[
            _mk_settlement("Weissfjord", "capital", 0.24, 0.16, "Silver-fjord town."),
            _mk_settlement("Frostmouth", "port", 0.20, 0.20, "Southern port of the barony; open six months a year."),
        ],
    ),

    # =============== VASSALS OF QADI-SHARR (3) ===============
    dict(
        id="ez_kahar", name="Emirate of Ez-Kahar", tier="emirate",
        color="#e2c078", overlord="qadi_sharr", religion="karnathi_sun",
        ruler="Emir Rashid ibn-Selim", ruler_title="Emir of Ez-Kahar",
        culture="Karnathi", motto="Gold is a Second Sun", founded="2E 402",
        army=34, economy=76,
        description="Wealthiest vassal of the Sultanate; hub of the Cinnamon Road.",
        lore=("Ez-Kahar is the chief caravan-city of the Cinnamon Road, and its emirs "
              "have historically been the sultanate's richest subjects. The current "
              "emir, Rashid, is a cousin of the sultan and a private patron of the "
              "sun-glass artisans."),
        seed_points=[(0.60, 0.38), (0.62, 0.34)],
        settlements=[
            _mk_settlement("Ez-Kahar", "capital", 0.60, 0.38, "Caravan-city of gilded courtyards."),
            _mk_settlement("Sunstop", "town", 0.62, 0.34, "Way-town on the Cinnamon Road."),
        ],
    ),
    dict(
        id="tamur", name="Beylik of Tamûr", tier="beylik",
        color="#d9a955", overlord="qadi_sharr", religion="karnathi_sun",
        ruler="Bey Yosef ibn-Halim", ruler_title="Bey of Tamûr",
        culture="Karnathi", motto="Where the Palms Meet, We Rest", founded="2E 411",
        army=24, economy=44,
        description="Oasis-beylik of the western desert.",
        lore=("Tamûr is a ring of date-palms around the great oasis of Tamûr-al-Sarr, "
              "and its bey holds hereditary rights over the oasis waters — a position "
              "of quiet power throughout the sultanate."),
        seed_points=[(0.44, 0.44), (0.46, 0.40)],
        settlements=[
            _mk_settlement("Tamûr", "capital", 0.44, 0.44, "Oasis-city ringed with date-palms."),
            _mk_settlement("Al-Sarr", "town", 0.46, 0.40, "Second oasis of the beylik."),
        ],
    ),
    dict(
        id="selkanth", name="Waziriate of Selkanth", tier="waziriate",
        color="#c69146", overlord="qadi_sharr", religion="karnathi_sun",
        ruler="Wazir Aisha bint-Ka", ruler_title="Wazir of Selkanth",
        culture="Karnathi", motto="Sun-Guard of the South", founded="2E 468",
        army=42, economy=38,
        description="Southern desert waziriate; the sultanate's military academy.",
        lore=("Selkanth trains the Muezzin-Guards — the warrior-priests who fight "
              "blindfold against shadow. Wazir Aisha is the first woman ever to hold "
              "the post; her appointment in 3E 884 caused a minor schism among the "
              "traditionalist muezzin."),
        seed_points=[(0.60, 0.48), (0.56, 0.52)],
        settlements=[
            _mk_settlement("Selkanth", "capital", 0.60, 0.48, "Southern city of blindfolded soldiers."),
            _mk_settlement("Fort Sun-Guard", "castle", 0.56, 0.52, "Academy-fortress of the Muezzin-Guards."),
        ],
    ),

    # =============== VASSALS OF SYLVAN REACH (3) ===============
    dict(
        id="hollowreach", name="Wardenship of Hollowreach", tier="wardenship",
        color="#5d7e46", overlord="sylvan_reach", religion="veyral",
        ruler="Warden Elish Hollowreach", ruler_title="Warden of Hollowreach",
        culture="Sylvan", motto="Watch the Roots", founded="2E 604",
        army=22, economy=28,
        description="Northern warden-realm of the Emberpine.",
        lore=("Hollowreach's wardens keep the northern paths of the Emberpine and are "
              "sworn to challenge any armed party that enters without leave. Their "
              "hereditary bow-guard, the Hollow-Watch, numbers just three hundred but "
              "is said to be worth ten times that number in the deepwood."),
        seed_points=[(0.14, 0.74)],
        settlements=[
            _mk_settlement("Hollowreach", "capital", 0.14, 0.74, "River-city on the Emberpine's northern edge."),
        ],
    ),
    dict(
        id="thornhaven", name="Enclave of Thornhaven", tier="enclave",
        color="#4b6e3a", overlord="sylvan_reach", religion="veyral",
        ruler="Speaker Osric Thornhaven", ruler_title="Speaker of Thornhaven",
        culture="Sylvan", motto="Thorns to the Outsider", founded="2E 691",
        army=20, economy=24,
        description="Fortified thorn-fen enclave; the Reach's southern shield.",
        lore=("Thornhaven's outer walls are living hedges of ironthorn, said to move "
              "against invaders. Its Speaker holds the ceremonial title of Shield of "
              "the Deepwood and is by tradition consulted before any war-vote of the "
              "Green Convocation."),
        seed_points=[(0.16, 0.86)],
        settlements=[
            _mk_settlement("Thornhaven", "capital", 0.16, 0.86, "Ironthorn-walled enclave."),
        ],
    ),
    dict(
        id="silverbough", name="Grove-Kingdom of Aelvarim", tier="grove_kingdom",
        color="#6a8f4d", overlord="sylvan_reach", religion="veyral",
        ruler="Grove-King Vaelith Aelvarim-Silverbough", ruler_title="Grove-King of Aelvarim",
        culture="Sylvan", motto="The Yew Holds", founded="1E 402",
        army=26, economy=32,
        description="Ancient grove-kingdom of the Aelvarim line; birthplace of the Veyral Path.",
        lore=("The Aelvarim line has kept the Mother-Yew for a thousand years; they are "
              "the only hereditary monarchy within the Sylvan Confederacy and by ancient "
              "compact provide the Speaker-in-Green in one out of every four terms."),
        seed_points=[(0.20, 0.78), (0.22, 0.82)],
        settlements=[
            _mk_settlement("Silverbough", "capital", 0.20, 0.78, "Silver-birch grove-town."),
            _mk_settlement("Yew-Fane", "holy_site", 0.22, 0.82, "The Mother-Yew — heart-shrine of the Veyral Path."),
        ],
    ),

    # =============== VASSALS OF SOLMYR (3) ===============
    dict(
        id="ostium", name="Prelacy of Ostium", tier="prelacy",
        color="#e8dcbb", overlord="solmyr", religion="ord_flame",
        ruler="Prelate Miriam Ostiar", ruler_title="Prelate of Ostium",
        culture="Solmyri", motto="Twelve Flames, Twelve Ports", founded="2E 004",
        army=28, economy=58,
        description="Southern port-prelacy of Solmyr; second city of the theocracy.",
        lore=("Ostium is the theocracy's window on the Rift Sea and its second-most "
              "populous city. Its Prelate is by ancient charter the second voice in "
              "the Conclave of Twelve and is traditionally next in line for the "
              "Ordinat's throne."),
        seed_points=[(0.60, 0.74), (0.56, 0.72)],
        settlements=[
            _mk_settlement("Ostium", "capital", 0.60, 0.74, "Southern port-prelacy."),
            _mk_settlement("Little Solmyr", "town", 0.56, 0.72, "Twin-town of Solmyr's poor pilgrims."),
        ],
    ),
    dict(
        id="kaldros", name="Templar-March of Kaldros", tier="templar_march",
        color="#d9c68a", overlord="solmyr", religion="ord_flame",
        ruler="Grand Templar Osrik Kaldros", ruler_title="Grand Templar of Kaldros",
        culture="Solmyri", motto="Steel for the Flame", founded="1E 302",
        army=68, economy=38,
        description="Militant order-state; the Ordinat's sword-arm.",
        lore=("Kaldros is technically a religious order, not a state; its Grand Templar "
              "is a life-appointed office. But by long tradition its lands are treated "
              "as a march of Solmyr. The current Grand Templar, Osrik, was raised at "
              "the same brotherhood as Ordinat Miriach XIV and is his personal ally."),
        seed_points=[(0.68, 0.60), (0.72, 0.62)],
        settlements=[
            _mk_settlement("Kaldros", "capital", 0.68, 0.62, "Militant seat of the Templars."),
            _mk_settlement("Templar's Keep", "castle", 0.72, 0.60, "Iron-flame fortress; training ground for the militant order."),
        ],
    ),
    dict(
        id="belkharim", name="Cantonment of Belkharim", tier="cantonment",
        color="#e8d3a4", overlord="solmyr", religion="ord_flame",
        ruler="Canton-Marshal Aelia Belkharim", ruler_title="Canton-Marshal",
        culture="Solmyri", motto="The Steppe Ends Here", founded="2E 812",
        army=44, economy=32,
        description="Frontier cantonment guarding Solmyr's eastern march against the steppe.",
        lore=("Belkharim was raised as a fortified cantonment in 2E 812 to hold back "
              "the raids of the Khanate of Uzarim, and its garrison has never in three "
              "centuries been reduced below full strength."),
        seed_points=[(0.72, 0.66), (0.74, 0.70)],
        settlements=[
            _mk_settlement("Belkharim", "capital", 0.72, 0.66, "Fortified cantonment-city."),
            _mk_settlement("East-Watch", "castle", 0.74, 0.70, "Watch-fort on the steppe road."),
        ],
    ),

    # =============== INDEPENDENT MINORS ~ 30+ ===============
    dict(
        id="vaenmark", name="Kingdom of Vaenmark", tier="kingdom",
        color="#7a4e3a", overlord=None, religion="stonefaith",
        ruler="King Radomir Vaen", ruler_title="King of Vaenmark",
        culture="Vaen", motto="The Highlands Endure", founded="2E 152",
        army=42, economy=44,
        description="Rugged highland kingdom of the Karim range; last of the free stone-kings.",
        lore=("Vaenmark is the last stone-king realm outside Volmarr's orbit — a rugged "
              "highland kingdom of terraced barley and long feuds. It has resisted "
              "Orthengardian annexation three times, always at ruinous cost. King "
              "Radomir has secretly negotiated a defensive pact with the Sultan of "
              "Qadi-Sharr — a fact no Orthengardian spymaster yet knows."),
        seed_points=[(0.36, 0.24), (0.40, 0.28), (0.34, 0.30)],
        settlements=[
            _mk_settlement("Vaenrahal", "capital", 0.36, 0.26, "Terraced highland capital of dry-stone."),
            _mk_settlement("Karim-Reach", "town", 0.40, 0.28, "Barley-town of the eastern slopes."),
            _mk_settlement("Fort Vaen", "castle", 0.34, 0.30, "Guarding the pass to the plains."),
        ],
    ),
    dict(
        id="threnwold", name="Grand Duchy of Threnwold", tier="grand_duchy",
        color="#5f7c47", overlord=None, religion="ord_flame",
        ruler="Grand Duke Halvar Threnwold", ruler_title="Grand Duke of Threnwold",
        culture="Threnwoldic", motto="Old Woods, Older Oaths", founded="2E 077",
        army=36, economy=42,
        description="Wooded grand duchy between the Iron Spine and the Karim Highlands.",
        lore=("Threnwold's grand dukes have kept their independence by playing the "
              "empire and Vaenmark against one another for six centuries. The current "
              "Grand Duke, Halvar, is famed for a personal library of six thousand "
              "scrolls — the largest secular collection in Kelvaros."),
        seed_points=[(0.50, 0.24), (0.46, 0.28)],
        settlements=[
            _mk_settlement("Threnwold", "capital", 0.50, 0.24, "Wooded capital of long-halls and cloisters."),
            _mk_settlement("Oakford", "town", 0.46, 0.28, "River-town of oak-timber wrights."),
        ],
    ),
    dict(
        id="merevault", name="Free City of Merevault", tier="free_city",
        color="#6b8ea3", overlord=None, religion="deep_fathom",
        ruler="Doge Kavric Merethim", ruler_title="Doge of Merevault",
        culture="Merevaulti", motto="The Fathom Provides", founded="2E 511",
        army=14, economy=64,
        description="Coast-city republic of the Deep Fathom cult; famed navy for hire.",
        lore=("Merevault's Doges are elected for life by the Fathom-Council of ship-"
              "captains and its navy — small but expert — is available to any bidder. "
              "The city venerates the Drowned King openly, a fact that makes visiting "
              "Ordinion clerics deeply uncomfortable."),
        seed_points=[(0.28, 0.36), (0.30, 0.40)],
        settlements=[
            _mk_settlement("Merevault", "capital", 0.28, 0.38, "Sea-city of black stone piers."),
            _mk_settlement("Fathom's Rest", "port", 0.30, 0.40, "Southern port of the Doge's navy."),
        ],
    ),
    dict(
        id="sarkathil", name="Republic of Sarkathil", tier="republic",
        color="#a5c9c1", overlord=None, religion="ord_flame",
        ruler="First Consul Amarath Sarkath", ruler_title="First Consul",
        culture="Sarkathi", motto="Coin, Council, Compass", founded="2E 618",
        army=18, economy=68,
        description="Merchant-republic on the Rift Sea; hires the Grey Wardens as its army.",
        lore=("Sarkathil is ruled by an elected First Consul and a Council of Fifty. "
              "It maintains no standing army but retains the mercenary Grey Wardens on "
              "permanent contract — an arrangement that has held for one hundred and "
              "forty years."),
        seed_points=[(0.34, 0.62), (0.36, 0.58)],
        settlements=[
            _mk_settlement("Sarkathil", "capital", 0.34, 0.60, "Merchant-republic; concentric harbours."),
            _mk_settlement("Little Sark", "town", 0.36, 0.58, "Wine-country town of the inland Republic."),
        ],
    ),
    dict(
        id="andros_vel", name="Kingdom of Andros-Vel", tier="kingdom",
        color="#a8763c", overlord=None, religion="ord_flame",
        ruler="Queen Ulyria Andros-Vel", ruler_title="Queen of Andros-Vel",
        culture="Andros", motto="Small Realm, Long Sword", founded="2E 289",
        army=28, economy=38,
        description="Central small kingdom, wedged between empires; famed swordsmiths.",
        lore=("Andros-Vel's blade-smiths forge the finest swords in Kelvaros; every "
              "Ordinion Templar carries an Andros blade at ordination. Queen Ulyria has "
              "reigned for thirty-one years by playing all four neighbouring giants against "
              "one another with a diplomat's genius bordering on witchcraft."),
        seed_points=[(0.44, 0.36), (0.42, 0.32)],
        settlements=[
            _mk_settlement("Andros-Vel", "capital", 0.44, 0.36, "Blade-city of ringing forges."),
            _mk_settlement("Vel-Cross", "town", 0.42, 0.32, "Northern crossing-town."),
        ],
    ),
    dict(
        id="corregar", name="Duchy of Corregar", tier="duchy",
        color="#7d5a45", overlord=None, religion="ord_flame",
        ruler="Duke Tallis Corregar", ruler_title="Duke of Corregar",
        culture="Corregar", motto="The Gate Stands", founded="2E 402",
        army=22, economy=30,
        description="Small border-duchy at the empire's western march.",
        lore=("Corregar is a buffer duchy that has changed hands between Orthengard and "
              "Vaenmark eleven times over four centuries. Duke Tallis is the first ruler "
              "in living memory to be trusted by both empires simultaneously."),
        seed_points=[(0.58, 0.22)],
        settlements=[
            _mk_settlement("Corregar", "capital", 0.58, 0.22, "Grey-walled buffer city."),
        ],
    ),
    dict(
        id="halgart", name="Prince-Bishopric of Halgart", tier="prince_bishopric",
        color="#b8a56c", overlord=None, religion="ord_flame",
        ruler="Prince-Bishop Elder Kaerath", ruler_title="Prince-Bishop of Halgart",
        culture="Solmyri", motto="Crozier and Crown", founded="2E 559",
        army=18, economy=34,
        description="Small church-state where the bishop is also secular sovereign.",
        lore=("Halgart was elevated to independent prince-bishopric in 2E 559 as a "
              "reward for the local bishop's heroic defence against Ashen Covenant "
              "heretics. Its ruler is elected for life by the Cathedral Chapter."),
        seed_points=[(0.62, 0.54)],
        settlements=[
            _mk_settlement("Halgart", "capital", 0.62, 0.54, "Small cathedral-city; bishop-throne beneath a bronze dome."),
        ],
    ),
    dict(
        id="marreth", name="County of Marreth", tier="county",
        color="#a89f6a", overlord=None, religion="ord_flame",
        ruler="Count Aldwyn Marreth", ruler_title="Count of Marreth",
        culture="Marreth", motto="Small but Sworn", founded="2E 622",
        army=10, economy=22,
        description="Tiny independent county; the smallest sovereign realm on the continent.",
        lore=("Marreth is Kelvaros's smallest sovereign realm — a single fortified town "
              "and its fields, sworn to no crown since 2E 622 when Count Aldwyn's "
              "great-grandfather refused vassalage to Orthengard and paid an enormous "
              "sum for perpetual charter."),
        seed_points=[(0.66, 0.50)],
        settlements=[
            _mk_settlement("Marreth", "capital", 0.66, 0.50, "One town, one wall, one banner."),
        ],
    ),
    dict(
        id="braeg", name="Fenlands Domain of Braeg", tier="domain",
        color="#5a6b45", overlord=None, religion="dhrenic",
        ruler="Fen-Lord Osric of Braeg", ruler_title="Fen-Lord of Braeg",
        culture="Fenlander", motto="The Fen Keeps its Secrets", founded="1E 802",
        army=14, economy=18,
        description="Marshland lord of the Whispering Fens.",
        lore=("Braeg's fen-lords rule from a floating hall on Osric's Mere and are "
              "reputed to keep the last living speaker of the Old Fen Tongue as their "
              "seneschal. Outsiders enter the fen at peril: the fen-lords levy no "
              "tolls, but the Fen itself is said to."),
        seed_points=[(0.48, 0.90), (0.52, 0.94)],
        settlements=[
            _mk_settlement("Osric's Hall", "capital", 0.48, 0.90, "Floating longhall on the mere."),
            _mk_settlement("Deep-Fen", "village", 0.52, 0.94, "Village of stilt-houses."),
        ],
    ),
    dict(
        id="windward", name="Kingdom of the Windward Isles", tier="kingdom",
        color="#7a9db6", overlord=None, religion="deep_fathom",
        ruler="Sea-King Halvard Windward", ruler_title="Sea-King of the Windward Isles",
        culture="Isleman", motto="Sail with the Storm", founded="2E 154",
        army=28, economy=44,
        description="Island kingdom of the western sea; wave-riders and grey-sailed corsairs.",
        lore=("The Windward Isles are ruled by an elected Sea-King chosen once every "
              "seven years by the captains of the Fifty-Longships. The current Sea-King, "
              "Halvard, is on his third and final term and is expected to abdicate at "
              "the next Council of Sails."),
        seed_points=[(0.16, 0.46), (0.14, 0.42), (0.10, 0.40)],
        settlements=[
            _mk_settlement("Windward", "capital", 0.16, 0.46, "Isle-capital of grey sails.",
                "Windward is built on the crescent-cliffs of the Isle of Kraevor. Its "
                "harbour holds the Fifty-Longships that give the Sea-Kingship its title."),
            _mk_settlement("Kraevorport", "port", 0.14, 0.42, "Northern port of the isles."),
            _mk_settlement("Little-Isle", "village", 0.10, 0.40, "Fishing hamlet on a smaller isle."),
        ],
    ),
    dict(
        id="ossanic", name="Free Kingdom of Ossanic", tier="free_kingdom",
        color="#8a7b45", overlord=None, religion="deep_fathom",
        ruler="Captain-King Roric Ossanim", ruler_title="Captain-King of Ossanic",
        culture="Corsair", motto="No Flag, No Master, No Rope", founded="3E 402",
        army=22, economy=32,
        description="Pirate-kingdom of the Sea of Wrecks; sworn to no crown.",
        lore=("Ossanic was founded when the corsair Roric the Elder seized the rocky "
              "outcrop of the Fenwyrm Isle and declared himself a king. The kingdom's "
              "constitution — such as it is — permits any captain of three or more "
              "ships a vote in council. Ordinion, Orthengard and Volmarr have all sent "
              "punitive fleets; none have found the corsair-haven."),
        seed_points=[(0.06, 0.74)],
        settlements=[
            _mk_settlement("Ossanic", "capital", 0.06, 0.74, "Cove-town of black masts."),
        ],
    ),
    dict(
        id="zosk", name="Tribal Federation of Zosk", tier="federation",
        color="#8f6c4c", overlord=None, religion="dhrenic",
        ruler="Hetman Kurog of the Grey Horse", ruler_title="Grand Hetman of Zosk",
        culture="Zoskan", motto="The Horse Runs, the Grass Bends", founded="1E 654",
        army=48, economy=26,
        description="Confederation of steppe-tribes east of the Rift Sea.",
        lore=("Zosk is a shifting confederation of nine steppe-clans bound by the "
              "Grey-Horse Compact of 1E 654. The Grand Hetman is elected every four "
              "summers at the Great Moot on the Ashen Steppe. Zoskan light cavalry has "
              "sacked Belkharim twice and been repulsed twenty-three times."),
        seed_points=[(0.70, 0.56), (0.74, 0.58), (0.72, 0.62)],
        settlements=[
            _mk_settlement("Kurog's Moot", "capital", 0.72, 0.58, "Great Moot; mobile capital of felt-halls."),
            _mk_settlement("Grey-Horse Camp", "town", 0.70, 0.56, "Winter-camp of the Grey Horse clan."),
            _mk_settlement("Stonering", "village", 0.74, 0.62, "Ancient stone-ring shrine of the ancestors."),
        ],
    ),
    dict(
        id="uzarim", name="Khanate of Uzarim", tier="khanate",
        color="#9b7a4a", overlord=None, religion="dhrenic",
        ruler="Great Khan Berkut of Uzarim", ruler_title="Great Khan of Uzarim",
        culture="Uzari", motto="Under One Sky, One Khan", founded="2E 812",
        army=52, economy=28,
        description="Steppe khanate east of Zosk; larger and more centralised.",
        lore=("Uzarim is the larger of the two great steppe realms and has been the "
              "sword hanging over eastern Solmyr for a century. Great Khan Berkut "
              "acceded in 3E 887 and immediately doubled the standing horse-guard."),
        seed_points=[(0.80, 0.60), (0.84, 0.66)],
        settlements=[
            _mk_settlement("Uzarim-Ordu", "capital", 0.80, 0.60, "Great felt-city of the Khan."),
            _mk_settlement("Berkut's Camp", "town", 0.84, 0.66, "Southern outpost of the Khanate."),
        ],
    ),
    dict(
        id="halaqim", name="Emirate of Halaqim", tier="emirate",
        color="#c99a5c", overlord=None, religion="karnathi_sun",
        ruler="Emir Sarik ibn-Halaq", ruler_title="Emir of Halaqim",
        culture="Karnathi", motto="Beyond the Sultan, the Sun", founded="2E 704",
        army=20, economy=32,
        description="Small independent Karnathi emirate; heretical to Qadi-Sharr's doctrine.",
        lore=("Halaqim broke from the sultanate in 2E 704 over a dispute of the Muezzin "
              "succession. The emirate maintains its own line of Grand Muezzins and is "
              "considered spiritually schismatic. Qadi-Sharr has never reconquered it "
              "for fear of igniting a wider sun-doctrinal war."),
        seed_points=[(0.36, 0.48), (0.34, 0.44)],
        settlements=[
            _mk_settlement("Halaqim", "capital", 0.36, 0.48, "Schismatic sun-city."),
            _mk_settlement("Second-Sun", "town", 0.34, 0.44, "Northern town of Halaqim's dissident clergy."),
        ],
    ),
    dict(
        id="emberport", name="Free City of Emberport", tier="free_city",
        color="#c48a5a", overlord=None, religion="deep_fathom",
        ruler="Doge Vellin Ember", ruler_title="Doge of Emberport",
        culture="Emberi", motto="Every Wind Pays Toll", founded="2E 664",
        army=16, economy=72,
        description="Autonomous port city on the Emberline Coast.",
        lore=("Emberport is the busiest port on the southeastern coast and taxes every "
              "cargo that passes its lighthouses. Its Doge is elected annually by the "
              "Guild of Piers — an office notorious for its short life expectancy."),
        seed_points=[(0.86, 0.80)],
        settlements=[
            _mk_settlement("Emberport", "capital", 0.86, 0.80, "Amber-lit harbour city."),
        ],
    ),
    dict(
        id="grey_wardens", name="Ordermarch of the Grey Wardens", tier="order_march",
        color="#7e7d70", overlord=None, religion="ashen_cov",
        ruler="Warden-Marshal Kaerin the Grey", ruler_title="Warden-Marshal",
        culture="Grey", motto="For a Price, Any Cause", founded="3E 217",
        army=58, economy=34,
        description="Mercenary state; the finest hired swords in Kelvaros.",
        lore=("Founded by the ex-Templar Kaerin the Elder in 3E 217, the Grey Wardens "
              "are Kelvaros's most respected mercenary company. They have a permanent "
              "contract with the Republic of Sarkathil and secretly follow the Ashen "
              "Covenant — a fact known only to their inner Warden-Circle."),
        seed_points=[(0.42, 0.52), (0.44, 0.56)],
        settlements=[
            _mk_settlement("Grey-Warden's Rest", "capital", 0.42, 0.52, "Fortress-town of the Warden-Circle."),
            _mk_settlement("Ash-Vigil", "castle", 0.44, 0.56, "Cinder-blackened chapter-house."),
        ],
    ),
    dict(
        id="nakresh", name="Vampiric Duchy of Nakresh", tier="duchy",
        color="#3b1f2b", overlord=None, religion="ashen_cov",
        ruler="Duke Malviel of Nakresh", ruler_title="Blood-Duke of Nakresh",
        culture="Nakreshi", motto="Night is a Longer Day", founded="2E 902",
        army=32, economy=24,
        description="Dark duchy of the northern woods; ruled by an ageless bloodline.",
        lore=("Nakresh's ducal line has ruled without succession for eight hundred and "
              "twenty years — a fact the neighbouring realms studiously do not discuss. "
              "The current Duke, Malviel, was already Duke when the empire was founded. "
              "Nakreshi peasants pay a token blood-tithe every mid-winter; in exchange, "
              "no outside army has crossed their border in living memory."),
        seed_points=[(0.30, 0.20), (0.28, 0.24)],
        settlements=[
            _mk_settlement("Nakresh", "capital", 0.30, 0.20, "Black-turreted ducal city.",
                "Nakresh's ducal palace has thirteen towers, one for each Blood-Duke recognised "
                "by the Ashen Covenant. Their portraits hang in a long gallery — and, disturbingly, "
                "each portrait is signed by the same hand."),
            _mk_settlement("Weeping-Wood Keep", "castle", 0.28, 0.24, "Fortress in the weeping-wood."),
        ],
    ),
    dict(
        id="vhalarim", name="Necrotheocracy of Vhalarim", tier="necrotheocracy",
        color="#1f2833", overlord=None, religion="ashen_cov",
        ruler="Grave-Regent Sorix the Third", ruler_title="Grave-Regent",
        culture="Vhalari", motto="Ash Answers All", founded="3E 411",
        army=28, economy=20,
        description="Ashen Covenant homeland; ruled by grave-regents on behalf of the dead.",
        lore=("Vhalarim was founded in 3E 411 immediately after the Ordinion's "
              "excommunication of the Ashen Covenant. Its Grave-Regents rule 'on "
              "behalf of the honoured dead', who are consulted through elaborate "
              "cinder-rituals. Its neighbours consider it either an abomination or a "
              "convenient buffer, depending on the season."),
        seed_points=[(0.24, 0.28)],
        settlements=[
            _mk_settlement("Vhalarim", "capital", 0.24, 0.28, "Ash-city; the great cinder-cauldron always smokes."),
        ],
    ),
    dict(
        id="grumnar_kal", name="Deep-Hold of Grumnar Kal", tier="hold",
        color="#5a4a3a", overlord=None, religion="stonefaith",
        ruler="Deepwarden Balgrim of the Iron Beard", ruler_title="Deepwarden",
        culture="Grumnari", motto="Stone Above, Stone Below", founded="1E 022",
        army=36, economy=48,
        description="Mountain-hold carved into the Iron Spine; folk of long beards and longer memory.",
        lore=("Grumnar Kal is the oldest continuous polity in Kelvaros — founded in "
              "1E 022, before even the martyr-prophet Ordis. Its people carve their "
              "cities into the mountain roots and elect a Deepwarden for life. The "
              "hold has never been conquered; even Kaskan the Unbroken went around it."),
        seed_points=[(0.58, 0.16), (0.62, 0.18)],
        settlements=[
            _mk_settlement("Grumnar Kal", "capital", 0.58, 0.16, "The Deep-Hold; twelve halls carved into the Iron Spine."),
            _mk_settlement("Ironroot", "town", 0.62, 0.18, "Surface market of the Deep-Hold."),
        ],
    ),
    dict(
        id="ozarel", name="Wyrm-Cult of Ozarel", tier="cult_state",
        color="#8a2c2a", overlord=None, religion="wyrm_creed",
        ruler="Rust-Priest Vellim Ozarim", ruler_title="Rust-Priest of Ozarel",
        culture="Wyrmbound", motto="From Rust We Rise", founded="3E 704",
        army=24, economy=22,
        description="Hidden dragon-cult in the Drakenspur peaks; publicly outlawed.",
        lore=("Officially the Wyrm-Cult was extinguished by the Purging of 3E 702. In "
              "truth, its Rust-Priests fled to hidden shrines in the Drakenspur peaks "
              "where they still tend Ozarel's copper-wire altars. The cult claims to "
              "hold three of the dragon's shed scales as relics."),
        seed_points=[(0.78, 0.72), (0.82, 0.76)],
        settlements=[
            _mk_settlement("Rust-Fane", "capital", 0.78, 0.72, "Hidden shrine-city clinging to the peaks."),
            _mk_settlement("Copper-Wire Keep", "castle", 0.82, 0.76, "Cliff-fortress with copper-plated walls."),
        ],
    ),
    dict(
        id="emberline", name="Confederation of the Emberline", tier="confederation",
        color="#c46a4a", overlord=None, religion="ord_flame",
        ruler="First Speaker Tarion of Emberline", ruler_title="First Speaker",
        culture="Emberi", motto="Where Coast Meets Council", founded="2E 828",
        army=26, economy=48,
        description="Loose confederation of six coastal towns along the Emberline.",
        lore=("The Emberline Confederation binds six small port-towns under a rotating "
              "First Speaker. It is best known for keeping open trade routes to the "
              "island of Cerelith and for producing the amber-lantern glass beloved "
              "of the Ordinion clergy."),
        seed_points=[(0.82, 0.70), (0.84, 0.74), (0.86, 0.68)],
        settlements=[
            _mk_settlement("Emberhold", "capital", 0.82, 0.70, "Amber-glass capital of the Confederation."),
            _mk_settlement("Coast-Vellin", "port", 0.84, 0.74, "Second port of the Emberline."),
            _mk_settlement("Lantern-Keep", "castle", 0.86, 0.68, "Old lighthouse-fortress."),
        ],
    ),
    dict(
        id="cerelith", name="Merchant-Republic of Cerelith", tier="merchant_republic",
        color="#c98abe", overlord=None, religion="ord_flame",
        ruler="Council of Twelve Merchants", ruler_title="Merchant-Council of Cerelith",
        culture="Cerelithi", motto="Twelve Ledgers, One Sea", founded="2E 902",
        army=12, economy=82,
        description="Island merchant-republic in the Sea of Snakes.",
        lore=("Cerelith's island holds one of the richest merchant cities on the "
              "continent. Its ruling Council of Twelve is drawn from the twelve "
              "great trading houses, and the Council seat rotates monthly among them. "
              "The republic maintains no army — only an oversized navy."),
        seed_points=[(0.94, 0.66)],
        settlements=[
            _mk_settlement("Cerelith", "capital", 0.94, 0.66, "Island city of tiled roofs and twelve harbours.",
                "Cerelith's twelve harbours — one per merchant-house — are all bridged by white "
                "marble arches. The Council's chamber sits atop a thirteenth, unused bridge, which "
                "no one has ever explained."),
        ],
    ),
    dict(
        id="traxion", name="Free Republic of Traxion", tier="republic",
        color="#c4a35c", overlord=None, religion="ord_flame",
        ruler="First Consul Bellin Traxor", ruler_title="First Consul of Traxion",
        culture="Traxi", motto="For the Common Word", founded="3E 214",
        army=16, economy=30,
        description="Small landlocked republic; rare experiment in universal male suffrage.",
        lore=("Traxion is Kelvaros's political oddity: since 3E 214 every freeman over "
              "twenty may vote in its bi-annual moot. The neighbouring monarchies "
              "regard the arrangement as either dangerous heresy or comic novelty."),
        seed_points=[(0.38, 0.68)],
        settlements=[
            _mk_settlement("Traxion", "capital", 0.38, 0.68, "Small republican town of low walls and open forum."),
        ],
    ),
    dict(
        id="ghurr", name="Barbarian Confederacy of Ghurr", tier="confederacy",
        color="#5c4a30", overlord=None, religion="dhrenic",
        ruler="War-Chieftain Ghurr Ironmouth", ruler_title="War-Chieftain of Ghurr",
        culture="Ghurric", motto="Iron Teeth, Iron Word", founded="2E 018",
        army=54, economy=22,
        description="Northern barbarian confederacy of raiders and horse-clans.",
        lore=("The Ghurric confederacy has raided the Margraviate of Ostenmark every "
              "third summer for four hundred years. War-Chieftain Ghurr Ironmouth is "
              "the fourteenth chieftain to bear the name and the first in three "
              "generations to have subdued all nine clan-heads under a single banner."),
        seed_points=[(0.42, 0.02), (0.48, 0.04), (0.54, 0.06)],
        settlements=[
            _mk_settlement("Ironmouth-Camp", "capital", 0.48, 0.04, "Great war-camp; a hundred bonfires by night."),
            _mk_settlement("Ghurric Standing-Stones", "holy_site", 0.42, 0.02, "Ancient ancestor-stones."),
            _mk_settlement("Wolf-Watch", "village", 0.54, 0.06, "Border outpost against Ostenmark."),
        ],
    ),
    dict(
        id="vaesca", name="Isle-Kingdom of Vaesca", tier="kingdom",
        color="#a2c9a4", overlord=None, religion="veyral",
        ruler="Queen Ilyth of Vaesca", ruler_title="Queen of Vaesca",
        culture="Vaescan", motto="The Isle Answers Only to the Isle", founded="2E 122",
        army=18, economy=32,
        description="Green isle-kingdom in the Sea of Snakes; last matriarchal realm.",
        lore=("Vaesca has been ruled by an unbroken line of queens since 2E 122. Its "
              "constitution forbids a king from sitting the throne — a rule that has "
              "led to at least one recorded case of a queen-in-name-only crowning a "
              "girl-child of two."),
        seed_points=[(0.94, 0.54), (0.96, 0.58)],
        settlements=[
            _mk_settlement("Vaesca", "capital", 0.94, 0.54, "Green-tiled isle-capital."),
            _mk_settlement("South-Isle Port", "port", 0.96, 0.58, "Southern harbour of the isle."),
        ],
    ),
    dict(
        id="karth_ulgra", name="Free City of Karth-Ulgra", tier="free_city",
        color="#a4886a", overlord=None, religion="ord_flame",
        ruler="Burgomaster Ulgra Karthim", ruler_title="Burgomaster",
        culture="Karthi", motto="Neither Empire Nor Chain", founded="3E 011",
        army=14, economy=42,
        description="Border free city between Orthengard's western march and Vaenmark.",
        lore=("Karth-Ulgra sits at the crossroads of three great empires and has "
              "profited enormously by playing them against one another. Its "
              "burgomasters are elected for six years and are famed for their beards, "
              "which by long tradition must not be trimmed while in office."),
        seed_points=[(0.50, 0.16), (0.52, 0.20)],
        settlements=[
            _mk_settlement("Karth-Ulgra", "capital", 0.50, 0.18, "Border free city; three great gates."),
            _mk_settlement("Ulgra-Gate", "castle", 0.52, 0.20, "Southern gate-fortress."),
        ],
    ),
    dict(
        id="elmhold", name="Duchy of Elmhold", tier="duchy",
        color="#88a25c", overlord=None, religion="veyral",
        ruler="Duke Rhys Elmhold", ruler_title="Duke of Elmhold",
        culture="Elmi", motto="Rooted, Not Ruled", founded="2E 344",
        army=20, economy=28,
        description="Forest-edge duchy on the northern fringe of the Emberpine.",
        lore=("Elmhold is often called the Reach's shy cousin — it follows the Veyral "
              "Path but has never joined the Sylvan Confederacy, preferring quiet "
              "sovereignty. Duke Rhys is famous for his skill with the elm-longbow."),
        seed_points=[(0.28, 0.66), (0.30, 0.70)],
        settlements=[
            _mk_settlement("Elmhold", "capital", 0.28, 0.66, "Elm-shaded ducal town."),
            _mk_settlement("Elm-Cross", "town", 0.30, 0.70, "River crossing of the elms."),
        ],
    ),
    dict(
        id="thelmar", name="Principality of Thelmar", tier="principality",
        color="#a86464", overlord=None, religion="ord_flame",
        ruler="Prince Osric Thelmar", ruler_title="Prince of Thelmar",
        culture="Thelmi", motto="Coast, Crown, Cross", founded="2E 621",
        army=22, economy=42,
        description="Coastal principality with the finest fleet outside the majors.",
        lore=("Thelmar's princes have quietly built the fifth-strongest fleet in "
              "Kelvaros without attracting undue attention. Prince Osric is a maritime "
              "scholar who has personally circumnavigated the continent — a feat done "
              "only twice before."),
        seed_points=[(0.80, 0.44), (0.82, 0.48)],
        settlements=[
            _mk_settlement("Thelmar", "capital", 0.80, 0.44, "Blue-tiled coast-capital."),
            _mk_settlement("Osric's Port", "major_port", 0.82, 0.48, "The prince's fleet-harbour."),
        ],
    ),
    dict(
        id="corvath", name="Kingdom of Corvath", tier="kingdom",
        color="#647858", overlord=None, religion="veyral",
        ruler="King Ealdric Corvath", ruler_title="King of Corvath",
        culture="Corvathi", motto="Under Green Leaf", founded="2E 289",
        army=26, economy=32,
        description="Small forest-edge kingdom along the Verdant Marches.",
        lore=("Corvath's kings claim descent from the mythic Green Convocation itself "
              "and are crowned in a moonlit grove rather than a hall. Ealdric is the "
              "first Corvathi king in a century to have visited the Reach's Bloom-tide."),
        seed_points=[(0.36, 0.60), (0.34, 0.64)],
        settlements=[
            _mk_settlement("Corvath", "capital", 0.36, 0.60, "Small forest-crowned capital."),
            _mk_settlement("Green-Ford", "town", 0.34, 0.64, "River-ford of green stones."),
        ],
    ),
    dict(
        id="bracken_hollow", name="County of Bracken-Hollow", tier="county",
        color="#a29050", overlord=None, religion="ord_flame",
        ruler="Countess Milena Bracken", ruler_title="Countess of Bracken-Hollow",
        culture="Brackeni", motto="A Small Word, a Long Reach", founded="2E 812",
        army=8, economy=22,
        description="Tiny hollow-county nestled between marshes and forest.",
        lore=("Bracken-Hollow's countesses have ruled without heir-troubles by the "
              "curious practice of adopting their successor at the age of twelve, "
              "regardless of birth. Milena was so adopted; her successor already stands "
              "at her side."),
        seed_points=[(0.44, 0.80)],
        settlements=[
            _mk_settlement("Bracken-Hollow", "capital", 0.44, 0.80, "Marsh-edge hollow-town."),
        ],
    ),
    dict(
        id="wexil", name="Sultanate of Wexil", tier="sultanate",
        color="#c4995e", overlord=None, religion="karnathi_sun",
        ruler="Sultan Wexil-ka the Second", ruler_title="Sultan of Wexil",
        culture="Wexili", motto="Southern Sun, Northern Star", founded="2E 728",
        army=32, economy=44,
        description="Independent sultanate south of Qadi-Sharr; second Karnathi power.",
        lore=("Wexil broke from the sultanate in 2E 728 under Wexil-ka the Founder and "
              "has held its independence by the simple expedient of never fighting a "
              "war it could not win. Wexil-ka II is the seventh of his line; the "
              "sultans of Wexil name their heirs after themselves by tradition."),
        seed_points=[(0.50, 0.58), (0.54, 0.60)],
        settlements=[
            _mk_settlement("Wexil", "capital", 0.50, 0.58, "White-domed southern sun-city."),
            _mk_settlement("South-Sun", "town", 0.54, 0.60, "Trade-town of the southern desert-fringe."),
        ],
    ),
    dict(
        id="ordinion_march", name="Theocratic Marches of Ordinion", tier="theocratic_march",
        color="#dfd0a0", overlord=None, religion="ord_flame",
        ruler="March-Ordinat Aelith of Ordinion", ruler_title="March-Ordinat",
        culture="Solmyri", motto="The Flame Extends", founded="3E 402",
        army=22, economy=30,
        description="Frontier religious march; a Solmyri splinter that guards the north.",
        lore=("The Theocratic Marches were established in 3E 402 to guard the Ordinion "
              "faith along the northern border. Though nominally an autonomous ally of "
              "Solmyr, its March-Ordinat sits on the Conclave of Twelve — an oddity "
              "that has never quite been resolved by canon law."),
        seed_points=[(0.42, 0.44), (0.40, 0.48)],
        settlements=[
            _mk_settlement("Ordinion-March", "capital", 0.42, 0.44, "Cathedral-fortress-city of the March."),
            _mk_settlement("Flame-Watch", "castle", 0.40, 0.48, "Border fort of the northern march."),
        ],
    ),
    dict(
        id="hond", name="Demarchy of Hond", tier="demarchy",
        color="#bfb098", overlord=None, religion="ord_flame",
        ruler="Rotating Assembly of Freeholders", ruler_title="First-Elected of Hond",
        culture="Hondi", motto="By Lot, By Voice, By Law", founded="3E 044",
        army=10, economy=28,
        description="Democracy-by-lot; a strange experiment in southern Kelvaros.",
        lore=("Hond selects its First-Elected annually by lot from among its freeholders "
              "— a system considered eccentric but stable. The current First-Elected "
              "is a former baker named Wren Halfin who by all accounts is doing a "
              "surprisingly good job."),
        seed_points=[(0.70, 0.84)],
        settlements=[
            _mk_settlement("Hond", "capital", 0.70, 0.84, "Low-walled southern town of open forum."),
        ],
    ),
    dict(
        id="loxmor", name="Theocracy of Loxmor", tier="theocracy",
        color="#e5dfc4", overlord=None, religion="ord_flame",
        ruler="Hierarch Volusia of Loxmor", ruler_title="Hierarch of Loxmor",
        culture="Loxi", motto="Twelve Flames, One Rule", founded="2E 918",
        army=16, economy=30,
        description="Small orthodox theocracy sworn to the Ordinion but not to Solmyr.",
        lore=("Loxmor's hierarchs accept Solmyr's doctrine but not Solmyr's political "
              "primacy — an old schism that has never quite ripened into full break. "
              "Hierarch Volusia has ruled for thirty-two years and has quietly refused "
              "to attend the last four Conclaves of Twelve."),
        seed_points=[(0.76, 0.80)],
        settlements=[
            _mk_settlement("Loxmor", "capital", 0.76, 0.80, "White-domed hierarch-city."),
        ],
    ),
    dict(
        id="talabas", name="United Clans of Talabas", tier="clan_union",
        color="#a8724a", overlord=None, religion="dhrenic",
        ruler="Speaker of Twelve, Osrag Talabin", ruler_title="Speaker of Twelve",
        culture="Talabin", motto="Twelve Names, One Tongue", founded="2E 887",
        army=32, economy=28,
        description="Southeastern clan union of twelve tribes bound by common law.",
        lore=("Talabas is a rare tribal state that has adopted a written common law — "
              "the Talabin Compact of 2E 887. Its Speaker of Twelve rotates every two "
              "years among the twelve clan-heads; the current Speaker is a warrior-"
              "poet whose battle-verses have become popular even in Solmyr."),
        seed_points=[(0.68, 0.92), (0.72, 0.94)],
        settlements=[
            _mk_settlement("Talabas", "capital", 0.68, 0.92, "Twelve-clan capital of long-halls."),
            _mk_settlement("Compact-Stone", "holy_site", 0.72, 0.94, "Standing-stone of the Compact."),
        ],
    ),
    dict(
        id="mokhur_tan", name="Tribal Kingdom of Mokhur-Tan", tier="tribal_kingdom",
        color="#6f5a34", overlord=None, religion="dhrenic",
        ruler="King-Chief Mokhur the Younger", ruler_title="King-Chief of Mokhur-Tan",
        culture="Mokhuri", motto="The Old Bloods Bind Us", founded="2E 452",
        army=28, economy=22,
        description="Northern tribal kingdom of the far mountains.",
        lore=("Mokhur-Tan is a hereditary tribal monarchy whose king-chiefs are chosen "
              "from the eldest son of the eldest son. Mokhur the Younger is the eighth "
              "of his line and famed for having personally slain a snow-bear at fifteen."),
        seed_points=[(0.66, 0.02)],
        settlements=[
            _mk_settlement("Mokhur-Tan", "capital", 0.66, 0.02, "Cliff-perched northern capital."),
        ],
    ),
    dict(
        id="pridon", name="Broken Kingdom of Pridon", tier="broken_kingdom",
        color="#948a55", overlord=None, religion="stonefaith",
        ruler="Regent Council of Pridon", ruler_title="Regent Council",
        culture="Pridoni", motto="A Crown, Still Sought", founded="2E 902",
        army=18, economy=20,
        description="Kingdom without a king; ruled by a fractious regent council.",
        lore=("Pridon's last king died without heir in 3E 812 and its Regent Council "
              "has ruled — barely — for eighty years while three claimants press their "
              "rights in slow legal war. Every attempt to crown one has been vetoed by "
              "the other two. The population is by now philosophical."),
        seed_points=[(0.44, 0.72)],
        settlements=[
            _mk_settlement("Pridon", "capital", 0.44, 0.72, "Old capital of the kingdom without a king."),
        ],
    ),
    dict(
        id="dissenya", name="Technocratic Republic of Dissenya", tier="technocracy",
        color="#8fa5a5", overlord=None, religion="ord_flame",
        ruler="First Artificer Belloth Dissim", ruler_title="First Artificer",
        culture="Dissenyan", motto="Measure Twice, Build Once", founded="3E 611",
        army=14, economy=54,
        description="Republic ruled by its guild of clockwork-artificers.",
        lore=("Dissenya's Artificer-Council rules by the ancient guild-charter. Its "
              "clockwork mechanisms are the finest on the continent — every court "
              "clock in Kelvaros bears a Dissenyan artificer's mark. The First "
              "Artificer, Belloth, is also the finest bronzeworker of his generation."),
        seed_points=[(0.56, 0.78), (0.52, 0.82)],
        settlements=[
            _mk_settlement("Dissenya", "capital", 0.56, 0.78, "Republic of a thousand ringing clocks."),
            _mk_settlement("Artificer's Halls", "town", 0.52, 0.82, "Guild town of the great workshops."),
        ],
    ),
    dict(
        id="villivox", name="Plombulate of Villivox", tier="plombulate",
        color="#c58aae", overlord=None, religion="ord_flame",
        ruler="Plombulate-Elect Rossic of Villivox", ruler_title="Plombulate-Elect",
        culture="Villivorxi", motto="Lead is a Softer Iron", founded="3E 344",
        army=8, economy=42,
        description="Small island lead-mining state; a peculiar constitutional oddity.",
        lore=("Villivox is the only 'Plombulate' in Kelvaros — a form of government "
              "invented in 3E 344 by the lead-baron Rossic the Elder, in which the "
              "ruler is chosen by weighing the candidates in lead ingots on a great "
              "public scale. The heaviest candidate wins. It is unclear whether this "
              "is a joke or not, but it has held for five hundred and forty years."),
        seed_points=[(0.90, 0.58)],
        settlements=[
            _mk_settlement("Villivox", "capital", 0.90, 0.58, "Lead-tiled isle-city."),
        ],
    ),
    dict(
        id="jib_jib", name="Confederation of Jib-Jib", tier="confederation",
        color="#94a662", overlord=None, religion="veyral",
        ruler="Six Speakers of Jib-Jib", ruler_title="Six Speakers",
        culture="Jibbi", motto="The Small Voice, Six Times", founded="2E 728",
        army=14, economy=24,
        description="A confederation of six small forest towns known for their disagreeable politics.",
        lore=("Jib-Jib is named for the doubled-voice of its confederate speakers — six "
              "speakers who must all agree for any policy to pass. In practice they "
              "rarely do, and Jib-Jib is famously the slowest-moving state in Kelvaros. "
              "This is, according to its citizens, a feature."),
        seed_points=[(0.66, 0.78)],
        settlements=[
            _mk_settlement("Jib-Jib", "capital", 0.66, 0.78, "Six-speaker confederate town."),
        ],
    ),
    dict(
        id="drakenmarch", name="Empire of Drakenmarch", tier="empire",
        color="#b8722c", overlord=None, religion="wyrm_creed",
        ruler="Drake-Emperor Ozel-Ka the Elder", ruler_title="Drake-Emperor",
        culture="Drakenmarch", motto="Rust and Flame", founded="3E 704",
        army=62, economy=38,
        description="Long peninsula 'empire'; strongly linked to the Wyrmbound Creed.",
        lore=("Drakenmarch styles itself an empire though it holds barely more land "
              "than a large kingdom. Its Drake-Emperors have historically been the "
              "chief secular patrons of the Wyrmbound Creed, and the current ruler, "
              "Ozel-Ka the Elder, is rumoured to be the Rust-Priest of Ozarel's own "
              "half-brother — a claim officially denied on both sides."),
        seed_points=[(0.92, 0.86), (0.88, 0.90), (0.84, 0.86)],
        settlements=[
            _mk_settlement("Drakenmarch", "capital", 0.90, 0.88, "Copper-tiled peninsula capital."),
            _mk_settlement("Rust-Port", "port", 0.94, 0.84, "Copper-wire harbour."),
            _mk_settlement("Ozel-Keep", "castle", 0.84, 0.86, "Drake-emperor's inland stronghold."),
        ],
    ),
]


# ------------------------------- RELATIONS -----------------------------------
RELATIONS = [
    # Major rivalries and wars
    dict(a="orthengard", b="qadi_sharr", type="rivalry",
         description="Seven declared wars over the Iron Spine pass-fortresses; a cold hatred."),
    dict(a="orthengard", b="volmarr", type="rivalry",
         description="Old wolves eyeing each other; both remember the Sack of Ravnholt in 2E 611."),
    dict(a="solmyr", b="ord_ashen", type="war",   # dummy — will filter out non-existent
         description=""),
    dict(a="solmyr", b="vhalarim", type="war",
         description="Ongoing spiritual war; Solmyr excommunicated Vhalarim in 3E 411."),
    dict(a="solmyr", b="nakresh", type="rivalry",
         description="Solmyr suspects (correctly) that Nakresh shelters Ashen Covenant clerics."),
    dict(a="orthengard", b="ghurr", type="war",
         description="Perpetual frontier war; Ostenmark raided every third summer."),
    dict(a="solmyr", b="uzarim", type="war",
         description="Belkharim's garrison has held for a century against Uzari raids."),
    dict(a="qadi_sharr", b="halaqim", type="rivalry",
         description="Schism of the Muezzin-succession; centuries of quiet feud."),
    dict(a="qadi_sharr", b="sylvan_reach", type="rivalry",
         description="Desert-folk consider the Reach a shadow-haven; Reach considers desert-folk fanatics."),
    dict(a="ozarel", b="solmyr", type="rivalry",
         description="Solmyr's Purging of 3E 702 has never been forgiven; the Rust-Priests wait."),
    dict(a="drakenmarch", b="solmyr", type="rivalry",
         description="Drakenmarch shelters wyrm-cultists; Solmyr calls for their extradition."),

    # Alliances and formal pacts
    dict(a="orthengard", b="solmyr", type="alliance",
         description="Concord of the Twelvefold Throne: Solmyr crowns Orthengardian emperors."),
    dict(a="solmyr", b="kaldros", type="alliance",
         description="The Templar-March is Solmyr's sword; sacred alliance since 1E 302."),
    dict(a="volmarr", b="grumnar_kal", type="alliance",
         description="Old Stone Faith pact of the Hearth-Fires; mutual defence since 2E 400."),
    dict(a="vaenmark", b="qadi_sharr", type="alliance",
         description="Secret defensive pact against Orthengard; known to almost no one."),
    dict(a="sarkathil", b="grey_wardens", type="alliance",
         description="Permanent mercenary contract; renewed every eight years since 3E 217."),
    dict(a="sylvan_reach", b="corvath", type="alliance",
         description="Green-Leaf Pact: informal but respected veyral alliance."),
    dict(a="sylvan_reach", b="elmhold", type="alliance",
         description="Elmhold observes the Bough-Oath informally."),
    dict(a="drakenmarch", b="ozarel", type="alliance",
         description="Publicly denied; privately, family ties bind the Rust-Priest and Drake-Emperor."),

    # Trade pacts
    dict(a="cerelith", b="emberport", type="trade",
         description="The Amber-Silk Concord: exclusive trade of amber for silks."),
    dict(a="iskal", b="ez_kahar", type="trade",
         description="Cinnamon Road Compact: shared tariff schedule."),
    dict(a="thelmar", b="orthengard", type="trade",
         description="Fleet-share pact; Thelmari shipwrights build imperial hulls."),
    dict(a="ossanic", b="windward", type="trade",
         description="Corsair-brother pact; safe waters between the isles."),

    # Personal unions / marriages (future gameplay hooks)
    dict(a="kern_vareth", b="orthengard", type="personal_union",
         description="Ducal cadet branch of the imperial house."),
    dict(a="ravnhal", b="volmarr", type="personal_union",
         description="Duchess Ynga is King Halgar's niece."),
]


# Filter any relations that reference a non-existent nation id (defensive).
_valid_ids = {n["id"] for n in NATIONS}
RELATIONS = [r for r in RELATIONS if r["a"] in _valid_ids and r["b"] in _valid_ids]
