
import hassapi as hass
import random
import colorsys

class HallwayEffect(hass.Hass):

    areas = {
        "hallway": {
            "mode": "rgbw",
            "lights": {
                "light.downstairs_hallway_stele_1": {},
                "light.downstairs_hallway_stele_2": {},
                "light.downstairs_hallway_stele_3": {},
                "light.downstairs_hallway_stele_4": {},
                "light.downstairs_hallway_stele_5": {},
                "light.downstairs_hallway_stele_6": {},
                "light.downstairs_hallway_stele_7": {},
            },
        },
        "mancave": {
            "mode": "rgbw",
            "lights": {
                "light.mancave_corner_left": {},
                "light.mancave_corner_right": {},
                "light.mancave_death_zone": {},
            },
        },
        "living_room": {
            "mode": "monochromatic",
            "lights": {
                "light.living_room_ceiling_east_1": {},
                "light.living_room_ceiling_east_2": {},
                "light.living_room_ceiling_east_3": {},
                "light.living_room_ceiling_east_4": {},
                "light.living_room_ceiling_east_5": {},
                "light.living_room_ceiling_east_6": {},
                "light.living_room_ceiling_east_7": {},
                "light.living_room_ceiling_east_8": {},
                "light.living_room_ceiling_west_1": {},
                "light.living_room_ceiling_west_2": {},
                "light.living_room_ceiling_west_3": {},
                "light.living_room_ceiling_west_4": {},
                "light.living_room_ceiling_west_5": {},
                "light.living_room_ceiling_west_6": {},
            },
        },
    }


    def initialize(self):

        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')

        for area, data in self.areas.items():
            for light in data["lights"].values():
                light["effect_on"] = False
            trigger = f"input_boolean.{area}_effect"
            self.listen_state(self.state_change, trigger, attribute='all')

            
    def state_change(self, trigger, attribute, old, new, kwargs):
        self.log("state_change()", f"trigger={trigger}, attribute={attribute}, old={old}, new={new}, kwargs={kwargs}")

        area = trigger[14:-7]  # take <x> as "input_boolean.<x>_effect"
        self.log("state_change()", area)
        if new['state'] == "on":
            for light, data in self.areas[area]["lights"].items():
                old_state = self.get_state(light, attribute="all")
                data['states_old'] = old_state["state"]
                data['effect_on'] = True
                args = {"area": area, "light": light, "mode": self.areas[area]["mode"]}
                self.transition(args)
        else:
            for light, data in self.areas[area]["lights"].items():
                data["effect_on"] = False
                self.turn_off(light)            


    def transition(self, args):
        self.log("transition()", f"args={args}")

        area = args["area"]
        light = args["light"]
        mode = args["mode"]
        
        if self.areas[area]["lights"][light]["effect_on"]:
            if mode in ("rgb", "rgbw"):
                trans_time = random.randint(2, 4)
                rnd = random.random()
                color = colorsys.hsv_to_rgb(rnd, 1.0, 0.4)
                if mode in "rgbw":
                    color += (0.25,)
                data = {'transition': trans_time, f"{mode}_color": list(map(lambda x: x*255, color))}
            if mode == "monochromatic":
                trans_time = random.randint(2, 4)
                rnd = (random.random() * 24) - 12
                data = {'transition': trans_time, "brightness": 48 + rnd}
            self.log("transition()", f"data={data})")
            self.turn_on(light, **data)

            args = {"area": area, "light": light, "mode": mode}
            self.run_in(self.transition, data["transition"], **args)
