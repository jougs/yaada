from scene_manager import SceneManager

class BedroomLights(SceneManager):

    area = "Bedroom"

    lights = {
        "light.bedroom_floor": {"state": "on", "brightness": 255},
        "light.bedroom_bedside_window": {"state": "on", "brightness": 255, "xy_color": (0.358, 0.346)},
        "light.bedroom_bedside_door": {"state": "on", "brightness": 255, "xy_color": (0.358, 0.346)},
        "light.master_bedroom_rubber_tree": {"state": "on"},
        "light.master_bedroom_gift_box": {"state": "on"},
    }

    scenes = {
        "ambient": {
            'name': 'ambient',
            'icon': 'mdi:weather-night',
            'replaces': [],
            'lights': {
                "light.bedroom_floor": {"state": "on", "brightness": 64},
                "light.master_bedroom_gift_box": {"state": "on"},
            }
        },
        "main": {
            'name': 'Main',
            'icon': 'mdi:lightbulb',
            'replaces': ["readingwindow", "readingdoor"],
            'lights': {
                "light.bedroom_floor": {"state": "on", "brightness": 196},
                "light.bedroom_bedside_window": {"state": "on", "brightness": 196, "xy_color": (0.491, 0.39)},
                "light.bedroom_bedside_door": {"state": "on", "brightness": 196, "xy_color": (0.491, 0.39)},
            }
        },
        "readingwindow": {
            'name': 'readingwindow',
            'icon': 'mdi:arrow-down-bold-box-outline',
            'replaces': [],
            'lights': {
                "light.bedroom_bedside_window": {"state": "on", "brightness": 128, "xy_color": (0.491, 0.39)},
            }
        },
        "readingdoor": {
            'name': 'readingdoor',
            'icon': 'mdi:arrow-down-bold-box-outline',
            'replaces': [],
            'lights': {
                "light.bedroom_bedside_door": {"state": "on", "brightness": 128, "xy_color": (0.491, 0.39)},
            }
        },
    }

    buttons = {
        "master_bedroom_hallway_door_top_short": "main",
        "master_bedroom_bathroom_door_short": "main",
        "master_bedroom_balcony_door_top_right_short": "main",
        "master_bedroom_bedside_window_left_short": "main",
        "master_bedroom_bedside_window_right_short": "readingwindow",
        "master_bedroom_bedside_door_left_short": "readingdoor",
        "master_bedroom_bedside_door_right_short": "main",
    }
