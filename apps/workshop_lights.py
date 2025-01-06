from scene_manager import SceneManager

class WorkshopLights(SceneManager):

    area = "Workshop"

    lights = {
        "light.workshop_walkthrough": {"state": "on"},
        "light.workshop_bright": {"state": "on"},
    }

    scenes = {
        'ambient': {
            'name': 'ambient',
            'icon': 'mdi:weather-night',
            'replaces': [],
            'lights': {}
        },
        "walkthrough": {
            'name': 'walkthrough',
            'icon': 'mdi:lightbulb',
            'replaces': [],
            'lights': {
                "light.workshop_walkthrough": {"state": "on"},
            }
        },
        "work": {
            'name': 'work',
            'icon': 'mdi:account-hard-hat',
            'replaces': [],
            'lights': {
                "light.workshop_bright": {"state": "on"},
            }
        },
    }

    buttons = {
        "workshop_light_short": "walkthrough",
        "workshop_light_long": "work",
    }
