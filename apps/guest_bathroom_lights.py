from scene_manager import SceneManager

class GuestBathroomLights(SceneManager):

    area = 'Guest bathroom'

    lights = {
        'light.guest_bathroom_ceiling': {'state': 'on', 'brightness': 255},
        'light.guest_bathroom_mirror': {'state': 'on', 'brightness': 255},
        'light.guest_bathroom_recess': {'state': 'on', 'brightness': 255},
        'light.guest_bathroom_skylight': {'state': 'on', 'brightness': 255},
    }

    scenes = {
        'ambient': {
            'name': 'ambient',
            'icon': 'mdi:weather-night',
            'replaces': [],
            'lights': {}
        },
        'shower': {
            'name': 'shower',
            'icon': 'mdi:shower',
            'replaces': [],
            'lights': {
                'light.guest_bathroom_ceiling': {'state': 'on', 'brightness': 255},
                'light.guest_bathroom_mirror': {'state': 'on', 'brightness': 255},
                'light.guest_bathroom_recess': {'state': 'on', 'brightness': 96},
                'light.guest_bathroom_skylight': {'state': 'on', 'brightness': 96},
            }
        },
    }

    buttons = {
        'guest_room_guest_bathroom_door_short': 'shower',
    }
