
import hassapi as hass
import random
import colorsys

class HallwayEffect(hass.Hass):

    triggers = {
        "input_boolean.hallway_effect": {
            "light.downstairs_hallway_stele_1": {},
            "light.downstairs_hallway_stele_2": {},
            "light.downstairs_hallway_stele_3": {},
            "light.downstairs_hallway_stele_4": {},
            "light.downstairs_hallway_stele_5": {},
            "light.downstairs_hallway_stele_6": {},
            "light.downstairs_hallway_stele_7": {},
        },
        "input_boolean.mancave_effect": {
            "light.mancave_corner_left": {},
            "light.mancave_corner_right": {},
            "light.mancave_death_zone": {},

        }
    }
    
    def initialize(self):

        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')

        for trigger, lights in self.triggers.items():
            for light, data in lights.items():
                data["effect_on"] = False

            self.listen_state(self.state_change, trigger, attribute='all')

        
    def state_change(self, trigger, attribute, old, new, kwargs):

        self.log("state_change()", f"trigger={trigger}, attribute={attribute}, old={old}, new={new}, kwargs={kwargs}")

        if new['state'] == "on":
            for light, data in self.triggers[trigger].items():
                old_state = self.get_state(light, attribute="all")
                data['states_old'] = old_state["state"]
                data['effect_on'] = True
                self.transition({'trigger': trigger, 'light': light})
        else:
            for data in self.triggers[trigger].values():
                data["effect_on"] = False
        
            
    def transition(self, kwargs):

        self.log("transition()", kwargs)
        trigger = kwargs['trigger']
        light = kwargs['light']
        
        if self.triggers[trigger][light]["effect_on"]:
#            rnd = random.uniform(-0.05, 0.115)
#            if rnd < 0.0:
#                rnd += 1
            rnd = random.random()
            color = colorsys.hsv_to_rgb(rnd, 1.0, 0.4)
            trans_time = random.randint(3, 4)
#            data = {'transition': trans_time, "rgb_color": list(map(lambda x: x*255, color)), "brightness": 64}
#            data = {'transition': trans_time, "rgb_color": list(map(lambda x: x*255, color)), "brightness": 128}
            data = {'transition': trans_time, "rgb_color": list(map(lambda x: x*255, color))}
            self.log("transition()", f"data={data})")
            self.turn_on(light, **data)
            self.run_in(self.transition, trans_time, light=light, trigger=trigger)
