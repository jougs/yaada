import hassapi as hass
from time import sleep


class Doorbell(hass.Hass):

    lights = [
        "light.downstairs_hallway_stele_1",
        "light.downstairs_hallway_stele_2",
        "light.downstairs_hallway_stele_3",
        "light.downstairs_hallway_stele_4",
        "light.downstairs_hallway_stele_5",
        "light.downstairs_hallway_stele_6",
        "light.downstairs_hallway_stele_7",
    ]

    trans_time = 0.5

    def initialize(self):

        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')

        self.listen_state(self.trigger, "input_boolean.doorbell_effect", attribute='all')


    def trigger(self, trigger, attribute, old, new, kwargs):
        
        self.log("trigger()", f"trigger={trigger}, new={new}")

        if new["state"] == "off":
            return
        
        for light in reversed(self.lights):
            old_state = self.get_state(light, attribute="all")

            attributes = {
                'transition': self.trans_time,
                "rgbw_color": (255, 0, 0, 0),
                "brightness": 255,
            }
            self.turn_on(light, **attributes)

            if old_state['state'] == "on":
                attributes = {"transition": self.trans_time}
                for key in ("brightness", "rgbw_color", "brightness"):
                    attributes[key] = old_state["attributes"][key]
                self.run_in(self.turn_light_on, self.trans_time, light=light, attributes=attributes)
            else:
                self.run_in(self.turn_light_off, self.trans_time, light=light)

        self.set_state("input_boolean.doorbell_effect", state="off")


    def turn_light_on(self, kwargs):
        
        self.turn_on(kwargs["light"], **kwargs["attributes"])

    def turn_light_off(self, kwargs):
        self.turn_off(kwargs["light"], transition=self.trans_time)
