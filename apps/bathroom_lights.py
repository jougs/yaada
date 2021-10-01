from scene_manager import SceneManager

class BathroomLights(SceneManager):

    area = "Bathroom"

    lights = {
        "light.bathroom_throne": {"state": "on", "brightness": 255},
    }

    scenes = {
        "ambient": {
            'name': 'ambient',
            'icon': 'mdi:weather-night',
            'replaces': [],
            'lights': {}
        },
        "main": {
            'name': 'Main',
            'icon': 'mdi:arrow-down-bold-box-outline',
            'replaces': [],
            'lights': {
                "light.bathroom_throne": {"state": "on", "brightness": 255},
            }
        },
    }

    buttons = {
        "master_bathroom_bedroom_door_short": "main",
        "laundry_room_bathroom_door_bottom_short": "main",
    }
