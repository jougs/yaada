import hassapi as hass
from time import sleep


class Doorbell(hass.Hass):

    lights = [f"light.downstairs_hallway_stele_{i}" for i in range(1,8)]
    trans_time = 0.25

    def initialize(self):

        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')

        self.listen_event(self.trigger, 'MQTT_MESSAGE', topic='input', namespace='mqtt')

    def trigger(self, event_name, data, kwargs):

        if data['payload'] != "doorbell_short":
            return

        doorbell_state = self.get_state("input_select.doorbell_mode", attribute="state")

        if "Ring" in doorbell_state:
            self.turn_on("switch.doorbell") # Turns itself off again after 1.5s, see ESPHome config

        if "Visual" in doorbell_state:
            self.sequence(reversed(self.lights), (255, 0, 0, 0))

        msg_data = {
            "target": self.args["telegram_target"],
            "message": f"The doorbell rang!",
        }
        self.call_service("telegram_bot/send_message", **msg_data)


    def sequence(self, lights, color):

        for i, light in enumerate(lights):
            old_state = self.get_state(light, attribute="all")
            old_attrs = old_state["attributes"]

            attributes = {
                'transition': self.trans_time,
                "rgbw_color": color,
                "brightness": 255,
            }
            self.turn_on(light, **attributes)

            if old_state['state'] == "on":
                attributes = {"transition": self.trans_time} | {key: old_attrs[key] for key in ("brightness", "rgbw_color")}
                self.run_in(self.turn_light_on, self.trans_time, light=light, attributes=attributes)
            else:
                self.run_in(self.turn_light_off, self.trans_time, light=light)

    def turn_light_on(self, kwargs):

        self.turn_on(kwargs["light"], **kwargs["attributes"])

    def turn_light_off(self, kwargs):
        self.turn_off(kwargs["light"], transition=self.trans_time)
