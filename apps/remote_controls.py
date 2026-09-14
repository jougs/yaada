
from copy import copy

import hassapi as hass

class Tradfri_E1743:
    """IKEA Tradfri ON/OFF Switch E1743
    https://zigbee.blakadder.com/Ikea_E1743.html
    """
    buttons = {
        ("on",): "on",
        ("off",): "off",
        ("move", 1, 83, 0, 0): "off_long", 
        ("move_with_on_off", 0, 83): "on_long",
    }

class Tradfri_E1810:
    """IKEA Tradfri Remote Control E1810
    https://zigbee.blakadder.com/Ikea_E1810.html
    """
    buttons = {
        ("step_with_on_off",): "up",
        ("step",): "down",
        ("toggle",): "center",
        ("press", 256, 13, 0): "left",
        ("press", 257, 13, 0): "right",
    }

    
class MancaveRemote(Tradfri_E1743):
    topic = "mancave_musicbox/status"
    def on(self):
        self.mqtt_pub(self.topic, '{"event": "on"}')
    def off(self):
        self.mqtt_pub(self.topic, '{"event": "off"}')

class OfficeRemote(Tradfri_E1743):
    def on(self):
        self.turn_on("input_boolean.scene_office_main")
    def off(self):
        self.turn_off("input_boolean.scene_office_main")

class TableSawRemote(Tradfri_E1743):
    def on(self):
        self.select_option("input_select.blast_gate", "Table saw")
        self.turn_on("switch.furnace_room_ctrl_furnace_room_dust_collection")
    def off(self):
        self.turn_off("switch.furnace_room_ctrl_furnace_room_dust_collection")

class MitreSawRemote(Tradfri_E1743):
    def on(self):
        self.select_option("input_select.blast_gate", "Mitre saw")
        self.turn_on("switch.furnace_room_ctrl_furnace_room_dust_collection")
    def off(self):
        self.turn_off("switch.furnace_room_ctrl_furnace_room_dust_collection")

class MaslowRemote(Tradfri_E1743):
    def on(self):
        self.select_option("input_select.blast_gate", "Maslow")
        self.turn_on("switch.furnace_room_ctrl_furnace_room_dust_collection")
    def off(self):
        self.turn_off("switch.furnace_room_ctrl_furnace_room_dust_collection")

class BedroomRemote(Tradfri_E1743):
    def scene_input(self, scene_name):
        return "input_boolean.scene_master_bedroom_" + scene_name
    def on(self):
        self.turn_on(self.scene_input("main"))
        for scene in ("reading", "all_on"):
            self.turn_off(self.scene_input(scene))
    def off(self):
        for scene in ("reading", "all_on", "main", "ambient"):
            self.turn_off(self.scene_input(scene))
    def on_long(self):
        self.mqtt_pub('input', "master_bedroom_hallway_door_bottom_up_short")
    def off_long(self):
        self.mqtt_pub('input', "master_bedroom_hallway_door_bottom_down_short")

class SchopfRemote(Tradfri_E1743):
    def on(self):
        self.turn_on("input_boolean.scene_barn_main")
    def off(self):
        self.turn_off("input_boolean.scene_barn_main")
    def on_long(self):
        self.turn_on("input_boolean.scene_outdoor_frontyard")
    def off_long(self):
        self.turn_off("input_boolean.scene_outdoor_frontyard")


class LivingRoomRemote(Tradfri_E1810):
    def scene_input(self, scene_name):
        return "input_boolean.scene_living_area_" + scene_name
    def up(self):
        pass
    def down(self):
        pass
    def center(self):
        self.toggle(self.scene_input('all_on'))
    def left(self):
        pass
    def right(self):
        pass

##     def arrow_left_click(self):
##         self.hass.turn_on(self.scene_input('diningfull'))         
##     def arrow_left_hold(self):
##         self.hass.turn_on(self.scene_input('dining'))
##     def arrow_right_click(self):
##         self.hass.turn_on(self.scene_input('livingfull'))
##     def arrow_right_hold(self):
##         self.hass.turn_on(self.scene_input('chillout'))
##     def brightness_down_click(self):
##         scenes = ("chillout", "cooking", "dining", "bar", "full", "ambient")
##         for scene in scenes:
##             self.hass.turn_off(self.scene_input(scene))
##     def brightness_up_click(self):
##         self.hass.turn_on(self.scene_input('full'))
##     def toggle(self):
##         scenes = ("dining", "diningfull", "livingfull", "full")
##         for scene in scenes:
##             self.hass.turn_off(self.scene_input(scene))
##         scenes = ("chillout", "bar", "ambient")
##         for scene in scenes:
##             self.hass.turn_on(self.scene_input(scene))
##     def toggle_hold(self):
##         scenes = ("chillout", "bar", "dining", "diningfull", "livingfull", "full")
##         for scene in scenes:
##             self.hass.turn_off(self.scene_input(scene))
## 


class RemoteControls(hass.Hass):

    remotes = {
        "cc:cc:cc:ff:fe:e0:5c:39": LivingRoomRemote(),
        "cc:cc:cc:ff:fe:8f:80:22": MancaveRemote(),
        "04:cd:15:ff:fe:31:b7:98": OfficeRemote(),
        "b4:e3:f9:ff:fe:8e:a0:77": MaslowRemote(),
        "b4:e3:f9:ff:fe:8e:b0:7b": MitreSawRemote(),
        "b4:e3:f9:ff:fe:90:04:a9": TableSawRemote(),
        "b4:e3:f9:ff:fe:91:55:8c": BedroomRemote(),
        "04:cd:15:ff:fe:2f:cc:78": SchopfRemote(),
    }

    def initialize(self):

        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')

        for rc in self.remotes.values():
            rc.mqtt_pub = lambda t, p: self.call_service("mqtt/publish", topic=t, payload=p)
            rc.turn_on = lambda e: self.turn_on(e)
            rc.turn_off = lambda e: self.turn_off(e)
            rc.toggle = lambda e: self.toggle(e)
            rc.select_option = lambda s, o: self.select_option(s, o)

        self.listen_event(self.__on_zha_event, "zha_event")


    def __on_zha_event(self, event_name, data, kwargs):

        if "command" not in data or data["command"] == "attribute_updated":
            return

        try:
            device = data["device_ieee"].lower()
            rc = self.remotes[device]
            cmd = rc.buttons[tuple([data["command"]] + data["args"])]
            self.log("on_zha_event()", f"executing event '{cmd}' for '{device}'")
            getattr(rc, cmd)()
        except KeyError:
            self.log("on_zha_event()", f"unmapped remote control event: {data}")
