from scene_manager import SceneManager
    
class LivingAreaLights(SceneManager):

    area = "Living Area"
    
    lights = {
        "light.dining_room_bar_1": {"state": "on", "brightness": 255},
        "light.dining_room_bar_2": {"state": "on", "brightness": 255},
        "light.dining_room_bar_3": {"state": "on", "brightness": 255},
        "light.dining_room_bar_downlight": {"state": "on", "brightness": 255},
        "light.dining_room_dresser": {"state": "on"},
        "light.dining_room_fairy_balls": {"state": "on"},
        "light.dining_room_plant_stand": {"state": "on", "brightness": 255, "xy_color": (0.358, 0.346)},
        "light.dining_room_fairy_string": {"state": "on"},
        "light.dining_table_1": {"state": "on", "brightness": 255},
        "light.dining_table_2": {"state": "on", "brightness": 255},
        "light.dining_table_3": {"state": "on", "brightness": 255},
        "light.dining_table_4": {"state": "on", "brightness": 255},
        "light.dining_table_5": {"state": "on", "brightness": 255},
        "light.kitchen_bar_downlight": {"state": "on", "brightness": 255},
        "light.kitchen_downlight": {"state": "on", "brightness": 255},
        "light.kitchen_floor_cabinets": {"state": "on", "brightness": 255},
        "light.kitchen_hob": {"state": "on", "brightness": 255},
        "light.kitchen_wall_cabinet": {"state": "on", "brightness": 255},
        "light.living_room_ceiling_west": {"state": "on", "brightness": 255},
        "light.living_room_corner_shelf": {"state": "on", "brightness": 255, "xy_color": (0.358, 0.346)},
        "light.living_room_fireplace": {"state": "on", "brightness": 255},
        "light.living_room_paper_lamp": {"state": "on", "brightness": 255, "xy_color": (0.358, 0.346)},
        "light.living_room_palm_tree": {"state": "on"},
        "light.pantry_shelf": {"state": "on", "brightness": 255},
        "light.pantry_downlight": {"state": "on", "brightness": 255},
        "light.living_room_recliner": {"state": "on"},
    }

    scenes = {
        "cooking": { # 0
            'name': 'cooking',
            'icon': 'mdi:silverware-fork-knife',
            'replaces': ['bar'],
            'lights': {
                "light.kitchen_bar_downlight": {"state": "on", "brightness": 255},
                "light.kitchen_wall_cabinet": {"state": "on", "brightness": 255},
                "light.kitchen_floor_cabinets": {"state": "on", "brightness": 255},
                "light.kitchen_hob": {"state": "on", "brightness": 255},
                "light.kitchen_downlight": {"state": "on", "brightness": 255},
                "light.pantry_shelf": {"state": "on", "brightness": 96},
                "light.dining_room_bar_1": {"state": "on", "brightness": 128},
                "light.dining_room_bar_2": {"state": "on", "brightness": 128},
                "light.dining_room_bar_3": {"state": "on", "brightness": 128},
            }
        },        
        "bar": { # 2
            'name': 'bar',
            'icon': 'mdi:glass-cocktail',
            'replaces': ['cooking'],
            'lights': {
                "light.dining_room_bar_1": {"state": "on", "brightness": 10},
                "light.dining_room_bar_2": {"state": "on", "brightness": 8},
                "light.dining_room_bar_3": {"state": "on", "brightness": 6},
                "light.kitchen_bar_downlight": {"state": "on", "brightness": 96},
                "light.kitchen_wall_cabinet": {"state": "on", "brightness": 128},
                "light.kitchen_floor_cabinets": {"state": "on", "brightness": 128},
                "light.dining_room_fairy_string": {"state": "on"},
                "light.living_room_palm_tree": {"state": "on"},
            }
        },
        "dining": { # 1
            'name': 'dining',
            'icon': 'mdi:food',
            'replaces': ['diningfull'],
            'lights': {
                "light.dining_room_bar_downlight": {"state": "on", "brightness": 255},
                "light.dining_room_dresser": {"state": "on"},
                "light.dining_room_plant_stand": {"state": "on", "brightness": 255, "rgb_color": (255,128,0)},
                "light.dining_table_1": {"state": "on", "brightness": 64},
                "light.dining_table_2": {"state": "on", "brightness": 32},
                "light.dining_table_3": {"state": "on", "brightness": 48},
                "light.dining_table_4": {"state": "on", "brightness": 64},
                "light.dining_table_5": {"state": "on", "brightness": 76},
            }
        },
        "diningfull": { # 1
            'name': 'dining bright',
            'icon': 'mdi:sunglasses',
            'replaces': ['dining'],
            'lights': {
                "light.dining_room_bar_downlight": {"state": "on", "brightness": 255},
                "light.dining_room_dresser": {"state": "on"},
                "light.dining_room_plant_stand": {"state": "on", "brightness": 255, "xy_color": (0.358, 0.346)},
                "light.dining_table_1": {"state": "on", "brightness": 255},
                "light.dining_table_2": {"state": "on", "brightness": 255},
                "light.dining_table_3": {"state": "on", "brightness": 255},
                "light.dining_table_4": {"state": "on", "brightness": 255},
                "light.dining_table_5": {"state": "on", "brightness": 255},
            }
        },
        "chillout": { # 3
            'name': 'chillout',
            'icon': 'mdi:sofa',
            'replaces': ['livingfull'],
            'lights': {
                "light.kitchen_bar_downlight": {"state": "on", "brightness": 112},
                "light.kitchen_wall_cabinet": {"state": "on", "brightness": 64},
                "light.dining_room_plant_stand": {"state": "on", "brightness": 64, "rgb_color": (128,96,0)},
                "light.living_room_ceiling_west": {"state": "on", "brightness": 96},
                "light.living_room_corner_shelf": {"state": "on", "brightness": 128, "rgb_color": (255,128,0)},
                "light.living_room_fireplace": {"state": "on", "brightness": 128},
                "light.living_room_paper_lamp": {"state": "on", "brightness": 79, "xy_color": (0.491, 0.39)},
                "light.living_room_recliner": {"state": "on"},
            }
        },
        "livingfull": { # 3
            'name': 'living room bright',
            'icon': 'mdi:sunglasses',
            'replaces': ['chillout'],
            'lights': {
                "light.living_room_ceiling_west": {"state": "on", "brightness": 255},
                "light.living_room_corner_shelf": {"state": "on", "brightness": 255, "xy_color": (0.358, 0.346)},
                "light.living_room_fireplace": {"state": "on", "brightness": 255},
                "light.living_room_paper_lamp": {"state": "on", "brightness": 255, "xy_color": (0.358, 0.346)},
                "light.living_room_recliner": {"state": "on"},
            }
        },
        "ambient": { # 4
            'name': 'ambient',
            'icon': 'mdi:weather-night',
            'replaces': [],
            'lights': {
                "light.kitchen_wall_cabinet": {"state": "on", "brightness": 64},
                "light.kitchen_floor_cabinets": {"state": "on", "brightness": 64},
                "light.pantry_shelf": {"state": "on", "brightness": 64},
                "light.dining_room_fairy_balls": {"state": "on"},
                "light.dining_room_fairy_string": {"state": "on"},
                "light.dining_room_bar_downlight": {"state": "on", "brightness": 32},
                "light.kitchen_bar_downlight": {"state": "on", "brightness": 32},
                "light.living_room_corner_shelf": {"state": "on", "brightness": 48, "rgb_color": (64, 32, 8)},
                "light.living_room_fireplace": {"state": "on", "brightness": 48},
                "light.living_room_palm_tree": {"state": "on"},
            }
        },
    }

#[
#    ('all_on', False),    [ 1     1   ]
#    ('cooking', True),    [ 1   1   0 ]
#    ('dining',
#    ('bar',
#    ('chillout',
#    ('ambient',               
#    'all_off',            [ 0 0 0 0 0 ]
#                        -----------------
#                          [
#]
#
#
#class based design
#chillout = Scene(priority)
#
#chilout.dim()
#  multipliziert mit dimmstufe
#  bei binaerlampen toggle bei 50%

# dim+ only raises levels of lamps that are below
# dim- only lowers levels of lampt that are above
    
    buttons = {
        "kitchen_hallway_door_short": "cooking",
        "kitchen_hallway_door_long": "alloff",
        "kitchen_living_room_door_right_short": "cooking",
        "kitchen_living_room_door_left_short": "bar",
        "living_room_chimney_left_short": "chillout",
        "living_room_chimney_right_short": "dining",
        "living_room_balcony_door_right_short": "chillout",
    }
