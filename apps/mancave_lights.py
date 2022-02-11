from scene_manager import SceneManager

class MancaveLights(SceneManager):

    area = "Mancave"

    lights = {
        "light.mancave_ceiling_long_wall": {"state": "on", "brightness": 255},
        "light.mancave_ceiling_short_wall": {"state": "on", "brightness": 255},
        "light.mancave_corner_left": {"state": "on", "brightness": 255},
        "light.mancave_corner_right": {"state": "on", "brightness": 255},
        "light.mancave_boulder": {"state": "on", "brightness": 255},
        "light.mancave_base_camp": {"state": "on", "brightness": 255},
        "light.mancave_death_zone": {"state": "on", "brightness": 255},
        "light.mancave_table": {"state": "on", "brightness": 255},
    }

    scenes = {
        "ambient": {
            'name': 'ambient',
            'icon': 'mdi:weather-night',
            'replaces': [],
            'lights': {}
        },
        "rehearsal": {
            'name': 'rehearsal',
            'icon': 'mdi:guitar-electric',
            'replaces': [],
            'lights': {
                "light.mancave_corner_left": {"state": "on", "brightness": 255, "rgbw_color": (0,0,255,0)},
                "light.mancave_corner_right": {"state": "on", "brightness": 255, "rgbw_color": (0,255,0,0)},
                "light.mancave_table": {"state": "on", "brightness": 72},
                "light.mancave_death_zone": {"state": "on", "brightness": 255, "rgbw_color": (255,0,0,0)},
            }
        },
        "climbing": {
            'name': 'climbing',
            'icon': 'mdi:carabiner',
            'replaces': [],
            'lights': {
                "light.mancave_ceiling_long_wall": {"state": "on", "brightness": 255},
                "light.mancave_ceiling_short_wall": {"state": "on", "brightness": 255},
                "light.mancave_death_zone": {"state": "on", "brightness": 255, "rgbw_color": (255,0,0,255)},
            }
        },
    }

    buttons = {
        "mancave_hallway_door_right_short": "rehearsal",
        "mancave_hallway_door_right_long": "climbing",
    }
