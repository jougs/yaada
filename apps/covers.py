import json
import hassapi as hass

buttons = {
    "living_room_balcony_door": [
        "hmw_lc_bl1_dr_neq1415576"
    ],
    "guest_room_balcony_door": [
        "hmw_lc_bl1_dr_neq1415822"
    ],
    "office_window": [
        "hmw_lc_bl1_dr_neq1415654"
    ],
    "master_bedroom_balcony_door_bottom": [
        "hmw_lc_bl1_dr_neq1415586"
    ],
    "master_bedroom_fixed_glazing_top": [
        "hmw_lc_bl1_dr_neq1415382"
    ],
    "master_bedroom_fixed_glazing_bottom": [
        "hmw_lc_bl1_dr_neq1415661"  # brick wall
    ],
    "master_bedroom_hallway_door_bottom": [
        "hmw_lc_bl1_dr_neq1415586",  # balcony door
        "hmw_lc_bl1_dr_neq1415382",  # fixed glazing
        "hmw_lc_bl1_dr_neq1415661",  # brick wall
    ],
}

actions = {
    "up": "cover/open_cover",
    "down": "cover/close_cover",
    "stop": "cover/stop_cover",
}

class CoverManager(hass.Hass):


    def initialize(self):

        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')

        self.listen_event(self.button_press, 'MQTT_MESSAGE', topic='input', namespace='mqtt')

        self.actors = {}
        for button in buttons:
            buttons[button] = {"actors": buttons[button], "state": "off"}
            for actor in buttons[button]["actors"]:
                try:
                    self.actors[actor].append(button)
                except KeyError:
                    self.actors[actor] = [button]

        for actor in self.actors:
            self.listen_state(self.reset_state, f'cover.{actor}', attribute='working')

    def button_press(self, event_name, data, kwargs):

        button = data['payload'].rsplit("_", 2)
        if button[0] not in buttons:
            return

        msg = f'event_name={event_name}, data={data}, kwargs={kwargs}'
        self.log('button_press()', msg)

        action = button[1]
        if buttons[button[0]]["state"] == "on":
            state = "off"
            action = "stop"
        else:
            state = "on"
        
        for actor in buttons[button[0]]["actors"]:
            self.log('button_press()', f"{actor}: {action}")

            self.call_service(actions[action], entity_id=f"cover.{actor}")
            for button in self.actors[actor]:
                buttons[button]["state"] = state

    def reset_state(self, entity, attribute, old, new, kwargs):

        msg = f'entity={entity}, attribute={attribute}, old={old}, new={new}, kwargs={kwargs}'
        self.log('reset_state()', msg)

        if old == "Yes" and new == "No":
            for button in self.actors[entity.split(".")[1]]:
                self.log('reset_state()', f"{button}: off")
                buttons[button]["state"] = "off"
