from scene_manager import SceneManager

class BathroomLights(SceneManager):

    area = "Bathroom"

    lights = {
        "light.bathroom_bath_tub": {"state": "on", "brightness": 255},
        "light.bathroom_mirror": {"state": "on", "brightness": 255},
        "light.bathroom_shower": {"state": "on", "brightness": 255},
        "light.bathroom_shower_recess": {"state": "on", "brightness": 255},
        "light.bathroom_throne": {"state": "on", "brightness": 255},
        "light.bathroom_below_vanity": {"state": "on", "brightness": 255},
        "light.bathroom_vanity": {"state": "on", "brightness": 255},
        "light.bathroom_vanity_recess_left": {"state": "on", "brightness": 255},
        "light.bathroom_vanity_recess_right": {"state": "on", "brightness": 255},
    }

    scenes = {
        "ambient": {
            'name': 'ambient',
            'icon': 'mdi:weather-night',
            'replaces': [],
            'lights': {
                "light.bathroom_below_vanity": {"state": "on", "brightness": 128},
                "light.bathroom_shower_recess": {"state": "on", "brightness": 128},
            }
        },
        "main": {
            'name': 'Main',
            'icon': 'mdi:arrow-down-bold-box-outline',
            'replaces': ["bright"],
            'lights': {
                "light.bathroom_bath_tub": {"state": "on", "brightness": 128},
                "light.bathroom_mirror": {"state": "on", "brightness": 128},
                "light.bathroom_shower": {"state": "on", "brightness": 255},
                "light.bathroom_throne": {"state": "on", "brightness": 255},
                "light.bathroom_vanity": {"state": "on", "brightness": 128},
            }
        },
        "bright": {
            'name': 'Main',
            'icon': 'mdi:arrow-down-bold-box-outline',
            'replaces': ["main"],
            'lights': {
                "light.bathroom_bath_tub": {"state": "on", "brightness": 128},
                "light.bathroom_mirror": {"state": "on", "brightness": 255},
                "light.bathroom_shower": {"state": "on", "brightness": 255},
                "light.bathroom_throne": {"state": "on", "brightness": 255},
                "light.bathroom_vanity": {"state": "on", "brightness": 255},
            }
        },
    }

    buttons = {
        "master_bathroom_bedroom_door_short": "main",
        "master_bathroom_vanity_short": "bright",
        "laundry_room_bathroom_door_bottom_short": "main",
    }
