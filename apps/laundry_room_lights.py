from scene_manager import SceneManager

class LaundryRoomLights(SceneManager):

    area = "Laundry Room"

    lights = {
        "light.laundry_room_ceiling": {"state": "on"},
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
                "light.laundry_room_ceiling": {"state": "on"},
            }
        },
    }

    buttons = {
        "laundry_room_hallway_door_short": "main",
        "laundry_room_bathroom_door_top_short": "main",
        "laundry_room_balcony_door_left_short": "main",
    }
