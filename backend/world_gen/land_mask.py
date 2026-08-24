"""
Hand-authored land mask for the Continent of Kelvaros.
Coordinates normalized 0..1  (x right, y down)  matching base_map.webp (2000x1923).

The continent is expressed as a list of positive land polygons. Water bodies
(ocean, inland seas, big lakes) are the negative space between them.

I hand-traced these polygons against the base map to fit:
  * western ragged ocean coast + islands
  * northern great mountain belt
  * central desert/plains
  * central-south inland sea ("Rift Sea")
  * SW forests + mountains
  * SE mountainous peninsula
  * eastern mountains and coast
"""

# Main continent block (roughly - eastern 3/4 of the map)
MAIN_CONTINENT = [
    # Trace outer edge clockwise from NW
    (0.24, 0.02),
    (0.34, 0.00),
    (0.55, 0.00),
    (0.72, 0.02),
    (0.85, 0.03),
    (0.96, 0.05),
    (0.99, 0.12),
    (1.00, 0.22),
    (0.99, 0.34),
    (0.97, 0.45),
    (1.00, 0.55),
    (1.00, 0.68),
    (0.98, 0.78),
    (0.94, 0.86),
    (0.88, 0.92),
    (0.82, 0.97),
    (0.74, 1.00),
    (0.62, 1.00),
    (0.52, 1.00),
    (0.42, 0.99),
    (0.34, 0.95),
    (0.30, 0.87),
    # Inland Rift Sea inlet - south central water carved into land
    (0.32, 0.82),
    (0.28, 0.76),
    (0.25, 0.70),
    (0.28, 0.63),
    (0.34, 0.58),
    (0.38, 0.55),
    (0.41, 0.53),
    (0.44, 0.55),
    (0.46, 0.53),  # coming back up around inland sea
    (0.44, 0.49),
    (0.40, 0.48),
    (0.36, 0.47),
    (0.32, 0.45),
    (0.28, 0.42),
    (0.26, 0.38),
    (0.24, 0.32),
    (0.26, 0.26),
    (0.28, 0.20),
    (0.26, 0.14),
    (0.24, 0.02),
]

# NW peninsula (fjord kingdom) - a big finger sticking out to the northwest across the sea
NW_PENINSULA = [
    (0.13, 0.20),
    (0.18, 0.16),
    (0.24, 0.15),
    (0.26, 0.18),
    (0.25, 0.24),
    (0.22, 0.28),
    (0.17, 0.31),
    (0.12, 0.34),
    (0.08, 0.30),
    (0.08, 0.24),
    (0.11, 0.20),
    (0.13, 0.20),
]

# SW landmass - forests, mountains, southern coast
SW_LANDMASS = [
    (0.00, 0.55),
    (0.06, 0.52),
    (0.14, 0.55),
    (0.18, 0.60),
    (0.22, 0.66),
    (0.24, 0.72),
    (0.22, 0.80),
    (0.24, 0.88),
    (0.28, 0.95),
    (0.32, 1.00),
    (0.20, 1.00),
    (0.10, 0.98),
    (0.02, 0.92),
    (0.00, 0.80),
    (0.00, 0.55),
]

# Small western islands
ISLANDS = [
    # Isle of Kraevor (large west)
    [
        (0.13, 0.42),
        (0.17, 0.40),
        (0.20, 0.44),
        (0.20, 0.50),
        (0.17, 0.53),
        (0.14, 0.51),
        (0.12, 0.46),
        (0.13, 0.42),
    ],
    # Smaller isle 1
    [
        (0.09, 0.38),
        (0.12, 0.38),
        (0.12, 0.41),
        (0.09, 0.41),
        (0.09, 0.38),
    ],
    # Smaller isle 2
    [
        (0.05, 0.44),
        (0.08, 0.43),
        (0.09, 0.46),
        (0.06, 0.47),
        (0.05, 0.44),
    ],
    # Isle of the Fenwyrm (SW)
    [
        (0.02, 0.72),
        (0.06, 0.70),
        (0.08, 0.74),
        (0.06, 0.78),
        (0.02, 0.76),
        (0.02, 0.72),
    ],
]

# Combined list of land polygons
LAND_POLYGONS = [MAIN_CONTINENT, NW_PENINSULA, SW_LANDMASS] + ISLANDS


# Terrain zones for classifying provinces after Voronoi tessellation.
# Each zone is (name, terrain_type, polygon_normalized_coords)
# Provinces are assigned the terrain of the zone their centroid falls in.
TERRAIN_ZONES = [
    ("Frost Wastes", "mountain", [
        (0.34, 0.00), (0.62, 0.00), (0.72, 0.04), (0.72, 0.16), (0.55, 0.20),
        (0.42, 0.18), (0.34, 0.12), (0.34, 0.00),
    ]),
    ("Iron Spine Range", "mountain", [
        (0.55, 0.05), (0.85, 0.03), (0.96, 0.06), (0.99, 0.18), (0.95, 0.28),
        (0.82, 0.28), (0.68, 0.24), (0.55, 0.20), (0.55, 0.05),
    ]),
    ("Great Kelvaran Desert", "desert", [
        (0.36, 0.36), (0.60, 0.34), (0.68, 0.38), (0.66, 0.48), (0.58, 0.52),
        (0.46, 0.52), (0.36, 0.48), (0.32, 0.42), (0.36, 0.36),
    ]),
    ("Ashen Steppe", "plains", [
        (0.55, 0.52), (0.72, 0.52), (0.78, 0.58), (0.76, 0.68), (0.66, 0.72),
        (0.55, 0.72), (0.48, 0.66), (0.50, 0.58), (0.55, 0.52),
    ]),
    ("Emberpine Deepwood", "forest", [
        (0.02, 0.70), (0.20, 0.70), (0.24, 0.80), (0.22, 0.92), (0.14, 0.98),
        (0.04, 0.96), (0.00, 0.85), (0.02, 0.70),
    ]),
    ("Verdant Marches", "forest", [
        (0.36, 0.60), (0.48, 0.60), (0.52, 0.68), (0.48, 0.74), (0.38, 0.72),
        (0.32, 0.66), (0.36, 0.60),
    ]),
    ("Drakenspur Range", "mountain", [
        (0.72, 0.55), (0.88, 0.55), (0.94, 0.65), (0.92, 0.78), (0.82, 0.86),
        (0.72, 0.82), (0.66, 0.72), (0.72, 0.55),
    ]),
    ("Skalder Coast", "coast", [
        (0.24, 0.02), (0.34, 0.02), (0.32, 0.14), (0.26, 0.18), (0.24, 0.14),
        (0.24, 0.02),
    ]),
    ("Fjord Reach", "coast", [
        (0.08, 0.20), (0.26, 0.18), (0.28, 0.28), (0.20, 0.32), (0.12, 0.34),
        (0.08, 0.30), (0.08, 0.20),
    ]),
    ("Sunbaked Plains", "plains", [
        (0.60, 0.72), (0.78, 0.72), (0.84, 0.80), (0.82, 0.90), (0.70, 0.94),
        (0.60, 0.90), (0.55, 0.82), (0.60, 0.72),
    ]),
    ("Whispering Fens", "swamp", [
        (0.42, 0.86), (0.55, 0.86), (0.58, 0.94), (0.50, 0.98), (0.42, 0.94),
        (0.42, 0.86),
    ]),
    ("Karim Highlands", "hills", [
        (0.32, 0.22), (0.42, 0.22), (0.44, 0.32), (0.36, 0.38), (0.28, 0.34),
        (0.32, 0.22),
    ]),
]
