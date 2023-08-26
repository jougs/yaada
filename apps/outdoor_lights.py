from scene_manager import SceneManager

class OutdoorLights(SceneManager):

    area = "Outdoor"

    lights = {
        "light.front_yard": {"state": "on"},
        "light.balcony_light_east": {"state": "on"},
        "light.balcony_light_south": {"state": "on"},
        "light.facade_light_north": {"state": "on"},
        "light.entrance_door_floor": {"state": "on", "brightness": 255},
        "light.front_porch_floor": {"state": "on", "brightness": 255},
        "light.back_yard": {"state": "on"},
        "light.bedroom_terrace": {"state": "on"},
    }

    scenes = {
        "ambient": {
            'name': 'ambient',
            'icon': 'mdi:weather-night',
            'replaces': [],
            'lights': {
                "light.entrance_door_floor": {"state": "on", "brightness": 32},
                "light.front_porch_floor": {"state": "on", "brightness": 32},
            }
        },
        "balcony": {
            'name': 'balcony',
            'icon': 'mdi:outdoor-lamp',
            'replaces': [],
            'lights': {
                "light.balcony_light_east": {"state": "on"},
                "light.balcony_light_south": {"state": "on"},
            }
        },
        "frontyard": {
            'name': 'front yard',
            'icon': 'mdi:track-light',
            'replaces': [],
            'lights': {
                "light.front_yard": {"state": "on"},
            }
        },
        "backyard": {
            'name': 'back yard',
            'icon': 'mdi:track-light',
            'replaces': [],
            'lights': {
                "light.back_yard": {"state": "on"},
            }
        },        
        "bedroom_terrace": {
            'name': 'bedroom terrace',
            'icon': 'mdi:track-light',
            'replaces': [],
            'lights': {
                "light.bedroom_terrace": {"state": "on"},
            }
        },        
    }

    buttons = {
        "living_room_balcony_door_left_short": "balcony",
        "guest_room_balcony_door_left_short": "balcony",
        "downstairs_hallway_entrance_door_long": "frontyard",
        "laundry_room_balcony_door_right_short": "backyard",
        "master_bedroom_balcony_door_top_left_short": "bedroom_terrace",
    }
