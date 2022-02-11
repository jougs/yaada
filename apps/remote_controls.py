
import hassapi as hass
import mqttapi as mqtt

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
    def arrow_right_click(self):
        self.hass.turn_on(self.scene_input('livingfull'))
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
        self.brightness_down_click()
        self.hass.turn_off(self.scene_input('ambient'))


class MancaveLight():
    pass


class MancavePA():
    topic = "mancave_musicbox/status"
    def on(self):
        self.hass.log("PA on")
        self.hass.call_service("mqtt/publish", topic=self.topic, payload='{"event": "on"}')
    def off(self):
        self.hass.log("PA off")
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


class RemoteControls(hass.Hass):

    def initialize(self):

        self.remotes = {
            "zigbee2mqtt/0xccccccfffee05c39/action": LivingRoomRemote(),
            "zigbee2mqtt/0xec1bbdfffe7e8838/action": MancaveLight(),
            "zigbee2mqtt/0xccccccfffe8f8022/action": MancavePA(),
            "zigbee2mqtt/0xb4e3f9fffe91558c/action": BedroomRemote(),
        }

        for topic, remote in self.remotes.items():
            self.listen_event(self.zigbee_event, "MQTT_MESSAGE", topic=topic, namespace="mqtt")
            remote.hass = self

    def zigbee_event(self, event_name, data, kwargs):
        action = data['payload']
        if hasattr(self.remotes[data['topic']], action):
            getattr(self.remotes[data['topic']], action)()
