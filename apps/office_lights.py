from scene_manager import SceneManager

class OfficeLights(SceneManager):

    area = "Office"

    lights = {
        "light.office_ceiling": {"state": "on"},
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
            'icon': 'mdi:lightbulb',
            'replaces': ["readingwindow", "readingdoor"],
            'lights': {
                "light.office_ceiling": {"state": "on"},
            }
        },
    }

    buttons = {
        "office_hallway_door_short": "main",
    }
