
import hassapi as hass

# IKEA Tradfri E1810 (five buttons, round)
#  * arrow_left_click
#  * arrow_left_hold
#  * arrow_left_release
#  * arrow_right_click
#  * arrow_right_hold
#  * arrow_right_release
#  * bightness_down_click
#  * bightness_down_hold
#  * bightness_down_release
#  * bightness_up_click
#  * bightness_up_hold
#  * bightness_up_release
#  * toggle
#  * toggle_hold

# IKEA Tradfri E1743 (two buttons, square)
#  * on
#  * off
#  * brightness_move_up
#  * brightness_move_down
#  * brightness_stop


class LivingRoomRemote():
    def scene_input(self, scene_name):
        return "input_boolean.scene_living_area_" + scene_name
    def arrow_left_click(self):
        self.hass.turn_on(self.scene_input('diningfull'))
    def arrow_left_hold(self):
        self.hass.turn_on(self.scene_input('dining'))
    def arrow_right_click(self):
        self.hass.turn_on(self.scene_input('livingfull'))
    def arrow_right_hold(self):
        self.hass.turn_on(self.scene_input('chillout'))
    def brightness_down_click(self):
        scenes = ("chillout", "cooking", "dining", "bar", "full", "ambient")
        for scene in scenes:
            self.hass.turn_off(self.scene_input(scene))
    def brightness_up_click(self):
        self.hass.turn_on(self.scene_input('full'))
    def toggle(self):
        scenes = ("dining", "diningfull", "livingfull", "full")
        for scene in scenes:
            self.hass.turn_off(self.scene_input(scene))
        scenes = ("chillout", "bar", "ambient")
        for scene in scenes:
            self.hass.turn_on(self.scene_input(scene))
    def toggle_hold(self):
        scenes = ("chillout", "bar", "dining", "diningfull", "livingfull", "full")
        for scene in scenes:
            self.hass.turn_off(self.scene_input(scene))


class MancaveRemote():
    topic = "mancave_musicbox/status"
    def on(self):
        self.hass.log("MancaveRemote", "PA on")
        self.hass.call_service("mqtt/publish", topic=self.topic, payload='{"event": "on"}')
    def off(self):
        self.hass.log("MancaveRemote", "PA off")
        self.hass.call_service("mqtt/publish", topic=self.topic, payload='{"event": "off"}')


class BedroomRemote():
    def scene_input(self, scene_name):
        return "input_boolean.scene_bedroom_" + scene_name
    def on(self):
        scenes = ("main",)
        for scene in scenes:
            self.hass.turn_on(self.scene_input(scene))
        scenes = ("readingwindow", "readingdoor", "full")
        for scene in scenes:
            self.hass.turn_off(self.scene_input(scene))
    def off(self):
        scenes = ("readingwindow", "readingdoor", "full", "main", "ambient")
        for scene in scenes:
            self.hass.turn_off(self.scene_input(scene))
    def brightness_move_up(self):
        msg = "master_bedroom_hallway_door_bottom_up_short"
        self.hass.call_service("mqtt/publish", topic='input', payload=msg)
    def brightness_move_down(self):
        msg = "master_bedroom_hallway_door_bottom_down_short"
        self.hass.call_service("mqtt/publish", topic='input', payload=msg)


class TableSawRemote():
    def on(self):
        self.hass.select_option("input_select.blast_gate", "Table saw")
        self.hass.turn_on("switch.furnace_room_dust_collection")
    def off(self):
        self.hass.turn_off("switch.furnace_room_dust_collection")


class MitreSawRemote():
    def on(self):
        self.hass.select_option("input_select.blast_gate", "Mitre saw")
        self.hass.turn_on("switch.furnace_room_dust_collection")
    def off(self):
        self.hass.turn_off("switch.furnace_room_dust_collection")


class MaslowRemote():
    def on(self):
        self.hass.select_option("input_select.blast_gate", "Maslow")
        self.hass.turn_on("switch.furnace_room_dust_collection")
    def off(self):
        self.hass.turn_off("switch.furnace_room_dust_collection")


class SchopfRemote():
    def on(self):
        self.hass.turn_on("light.barn_main")
    def off(self):
        self.hass.turn_off("light.barn_main")
    def brightness_move_up(self):
        self.hass.turn_on("light.barn_chandelier_1")
        self.hass.turn_on("light.barn_chandelier_2")
    def brightness_move_down(self):
        self.hass.turn_off("light.barn_chandelier_1")
        self.hass.turn_off("light.barn_chandelier_2")


class OfficeRemote():
    def on(self):
        self.hass.turn_on("input_boolean.scene_office_main")
    def off(self):
        self.hass.turn_off("input_boolean.scene_office_main")



class RemoteControls(hass.Hass):

    remotes = {
        "living_room_remote_control": LivingRoomRemote(),
        "mancave_remote_control": MancaveRemote(),
        "bedroom_remote_control": BedroomRemote(),
        "shop_remote_control_table_saw": TableSawRemote(),
        "shop_remote_control_mitre_saw": MitreSawRemote(),
        "shop_remote_control_maslow": MaslowRemote(),
        "barn_remote_control": SchopfRemote(),
        "office_remote_control": OfficeRemote(),
    }


    def initialize(self):

        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')

        for remote_name, remote_cls in self.remotes.items():
            remote_cls.hass = self
            topic = f"zigbee2mqtt/{remote_name}/action"
            self.listen_event(self.on_event, 'MQTT_MESSAGE', topic=topic, namespace='mqtt')


    def on_event(self, event_name, data, kwargs):

        #self.log("on_event()", f"event_name={event_name}, data={data}, kwargs={kwargs}")

        remote = data["topic"].split("/")[1]
        command = data["payload"]

        self.log("on_event()", f"remote={remote}, command={command}")

        remote = self.remotes[remote]
        if hasattr(remote, command):
            getattr(remote, command)()
        else:
            self.log("on_event()", f"command {command} not mapped by remote control class!")
