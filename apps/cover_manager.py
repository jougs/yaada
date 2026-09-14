import json

import hassapi as hass
from collections import defaultdict


class CoverManager(hass.Hass):

    buttons = {                                   # HomeMatic  type / serial
        "living_room_balcony_door_bottom": [
            "living_room_shutter",                # hmw_lc_bl1_dr_neq1415576
        ],
        "guest_room_balcony_door_bottom": [
            "guest_room_shutter",                 # hmw_lc_bl1_dr_neq1415822
        ],
        "office_window": [
            "office_shutter",                     # hmw_lc_bl1_dr_neq1415654
        ],
        "master_bedroom_balcony_door_bottom": [
            "master_bedroom_shutter_left",        # hmw_lc_bl1_dr_neq1415586
        ],
        "master_bedroom_fixed_glazing_top": [
            "master_bedroom_shutter_right",       # hmw_lc_bl1_dr_neq1415382
        ],
        "master_bedroom_fixed_glazing_bottom": [
            "master_bedroom_shutter_brick_wall",  # hmw_lc_bl1_dr_neq1415661
        ],
        "master_bedroom_hallway_door_bottom": [
            "master_bedroom_shutter_left",        # hmw_lc_bl1_dr_neq1415586
            "master_bedroom_shutter_right",       # hmw_lc_bl1_dr_neq1415382
            "master_bedroom_shutter_brick_wall",  # hmw_lc_bl1_dr_neq1415661
        ],
    }

    actions = {
        "up": "cover/open_cover",
        "down": "cover/close_cover",
        "stop": "cover/stop_cover",
    }

    def initialize(self):

        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')

        self.listen_event(self.button_press, 'MQTT_MESSAGE', topic='input', namespace='mqtt')

        self.actors = defaultdict(list)
        for button_name, actors in self.buttons.items():
            for actor in actors:
                self.actors[actor].append(button_name)
        self.actors = dict(self.actors)

        self.buttons = {
            button_name: {"actors": actors, "state": "off"}
            for button_name, actors in self.buttons.items()
        }

        for actor in self.actors:
            self.listen_state(self.set_state, f'cover.{actor}', attribute='working')


    def button_press(self, event_name, data, kwargs):

        try:
            button_name, action, press_duration = data['payload'].rsplit("_", 2)
            button_data = self.buttons[button_name]
        except (ValueError, KeyError):
            return

        msg = f'event_name={event_name}, data={data}, kwargs={kwargs}'
        self.log('button_press()', msg)

        if button_data["state"] == "on":
            state = "off"
            action = "stop"
        else:
            state = "on"

        for actor in button_data["actors"]:
#            self.log('button_press()', f"{actor}: {action}")
            self.call_service(self.actions[action], entity_id=f"cover.{actor}")
            for button in self.actors[actor]:
                self.buttons[button]["state"] = state


    def set_state(self, entity, attribute, old, new, kwargs):

        state = {
            ("Yes", "No"): "off",
            ("Yes", "Yes"): "on",
            ("No", "No"): "off",
            ("No", "Yes"): "on",
        }[(old, new)]

        for button in self.actors[entity.split(".")[1]]:
#            self.log('set_state()', f"{button}: {state}")
            self.buttons[button]["state"] = state
