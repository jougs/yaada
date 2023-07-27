from scene_manager import SceneManager

class FurnaceRoomLights(SceneManager):

    area = "Furnace room"

    lights = {
        "light.furnace_room_sink_ceiling": {"state": "on"},
        "light.furnace_room_below_sink": {"state": "on", "brightness": 255},
        "light.furnace_room_buffer_tank": {"state": "on", "brightness": 255},
        "light.furnace_room_mixing_valves": {"state": "on", "brightness": 255},
        "light.furnace_room_wood_chips_top": {"state": "on", "brightness": 255},
        "light.furnace_room_wood_chips_right": {"state": "on", "brightness": 255},
        "light.furnace_room_wood_chips_bottom": {"state": "on", "brightness": 255},
        "light.furnace_room_wood_chips_left": {"state": "on", "brightness": 255},
        "light.furnace_room_belt_grinder": {"state": "on"},
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
            'replaces': [],
            'lights': {
                "light.furnace_room_sink_ceiling": {"state": "on"},
                "light.furnace_room_below_sink": {"state": "on", "brightness": 255},
                "light.furnace_room_buffer_tank": {"state": "on", "brightness": 255},
                "light.furnace_room_mixing_valves": {"state": "on", "brightness": 255},
                "light.furnace_room_wood_chips_bottom": {"state": "on", "brightness": 255},
                "light.furnace_room_belt_grinder": {"state": "on"},
            }
        },
    }

    buttons = {
        "furnace_room_backyard_door_right_short": "main",
    }
