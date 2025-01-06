from scene_manager import SceneManager

class BarnLights(SceneManager):

    area = "Barn"

    lights = {
        "light.barn_main": {"state": "on"},
    }

    scenes = {
        'ambient': {
            'name': 'ambient',
            'icon': 'mdi:weather-night',
            'replaces': [],
            'lights': {}
        },
        "main": {
            'name': 'main',
            'icon': 'mdi:barn',
            'replaces': [],
            'lights': {
                "light.barn_main": {"state": "on"},
            }
        },
    }

    buttons = {
        "barn_workshop_door_short": "main",
    }
