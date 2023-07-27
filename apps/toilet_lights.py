from scene_manager import SceneManager

class ToiletLights(SceneManager):

    area = "Toilet"

    lights = {
        "light.toilet_mirror": {"state": "on", "brightness": 255},
        "light.toilet_ledge": {"state": "on", "brightness": 255},
    }

    scenes = {
        "ambient": {
            'name': 'ambient',
            'icon': 'mdi:weather-night',
            'replaces': [],
            'lights': {
                "light.toilet_mirror": {"state": "on", "brightness": 64},
            }
        },
        "main": {
            'name': 'Main',
            'icon': 'mdi:arrow-down-bold-box-outline',
            'replaces': ["bright"],
            'lights': {
                "light.toilet_mirror": {"state": "on", "brightness": 255},
                "light.toilet_ledge": {"state": "on", "brightness": 255},
            }
        },
    }

    buttons = {
        "toilet_short": "main",
    }
