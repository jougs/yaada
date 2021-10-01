from scene_manager import SceneManager

class HallwayLights(SceneManager):

    area = "Hallway"

    lights = {
        "light.hallway_stairs": {"state": "on", "brightness": 255},
        "light.downstairs_hallway_nightlight": {"state": "on", "brightness": 255},
        "light.downstairs_hallway_ceiling": {"state": "on", "brightness": 255},
        "light.downstairs_hallway_stele_1": {"state": "on", "brightness": 255, "rgb_color": (255,224,160), "white_value": 196},
        "light.downstairs_hallway_stele_2": {"state": "on", "brightness": 255, "rgb_color": (255,224,160), "white_value": 196},
        "light.downstairs_hallway_stele_3": {"state": "on", "brightness": 255, "rgb_color": (255,224,160), "white_value": 196},
        "light.downstairs_hallway_stele_4": {"state": "on", "brightness": 255, "rgb_color": (255,224,160), "white_value": 196},
        "light.downstairs_hallway_stele_5": {"state": "on", "brightness": 255, "rgb_color": (255,224,160), "white_value": 196},
        "light.downstairs_hallway_stele_6": {"state": "on", "brightness": 255, "rgb_color": (255,224,160), "white_value": 196},
        "light.downstairs_hallway_stele_7": {"state": "on", "brightness": 255, "rgb_color": (255,224,160), "white_value": 196},
        "light.upstairs_hallway_corner": {"state": "on", "brightness": 255, "rgb_color": (255,224,160)},
        "light.upstairs_hallway_walls": {"state": "on"},
        "light.upstairs_hallway_giftbox": {"state": "on"},
        "light.upstairs_hallway_apothecary_cabinet": {"state": "on"},
        "light.guest_bathroom_skylight": {"state": "on", "brightness": 255},
    }

    scenes = {
        "ambient": {
            'name': 'ambient',
            'icon': 'mdi:weather-night',
            'replaces': [],
            'lights': {
                "light.hallway_stairs": {"state": "on", "brightness": 64},
                "light.downstairs_hallway_nightlight": {"state": "on", "brightness": 64},
                "light.upstairs_hallway_giftbox": {"state": "on"},
                "light.upstairs_hallway_apothecary_cabinet": {"state": "on"},
            }
        },
        "downstairs": {
            'name': 'downstairs',
            'icon': 'mdi:arrow-down-bold-box-outline',
            'replaces': [],
            'lights': {
                "light.hallway_stairs": {"state": "off"},
                "light.downstairs_hallway_nightlight": {"state": "off"},
                "light.downstairs_hallway_ceiling": {"state": "on", "brightness": 255},
                "light.downstairs_hallway_stele_1": {"state": "on", "brightness": 196, "rgb_color": (255,224,160)},
                "light.downstairs_hallway_stele_2": {"state": "on", "brightness": 196, "rgb_color": (255,224,160)},
                "light.downstairs_hallway_stele_3": {"state": "on", "brightness": 196, "rgb_color": (255,224,160)},
                "light.downstairs_hallway_stele_4": {"state": "on", "brightness": 196, "rgb_color": (255,224,160)},
                "light.downstairs_hallway_stele_5": {"state": "on", "brightness": 196, "rgb_color": (255,224,160)},
                "light.downstairs_hallway_stele_6": {"state": "on", "brightness": 196, "rgb_color": (255,224,160)},
                "light.downstairs_hallway_stele_7": {"state": "on", "brightness": 196, "rgb_color": (255,224,160)},
            }
        },
        "upstairs": {
            'name': 'upstairs',
            'icon': 'mdi:arrow-up-bold-box-outline',
            'replaces': [],
            'lights': {
                "light.upstairs_hallway_walls": {"state": "on"},
                "light.upstairs_hallway_apothecary_cabinet": {"state": "on"},
            }
        },
    }

    buttons = {
        "mancave_hallway_door_left_short": "upstairs",        
        "downstairs_hallway_entrance_door_short": "downstairs",
        "downstairs_hallway_office_door_short": "downstairs",
        "downstairs_hallway_laundry_room_door_short": "downstairs",
        "downstairs_hallway_boiler_room_door_short": "downstairs",
        "downstairs_hallway_workshop_door_bottom_short": "downstairs",
        "downstairs_hallway_workshop_door_top_short": "upstairs",
        "upstairs_hallway_guest_room_door_short": "upstairs",
        "upstairs_hallway_kitchen_door_short": "upstairs",
        "upstairs_hallway_stairs_short": "downstairs",
    }
