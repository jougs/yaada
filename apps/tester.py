import json
import hassapi as hass


class Tester(hass.Hass):

    lights = {
        "light.diningroom_bar1_light": {"state": "on", "brightness": 255},
    }
    
    buttons = {
        "input/kitchen_hallwaydoor": "cooking",
    }
    
    def initialize(self):
        """Initialize the App

        This function is run upon a restart of AppDaemon or Home
        Assistant. Its main task is to register listerners for manual
        state changes, (zigbee) button presses and changes in the
        scene selection.

        Upon a restart of Home Assistant, this function will
        reconstruct the scene stack correctly, however with the
        limitation of loosing the ordering of scenes in the stack.

        """

        for light in self.lights.keys():
            self.listen_state(self.state_change, light, attribute="state")

        for button in self.buttons:
            self.listen_event(self.button_press, "MQTT_MESSAGE", topic=button, namespace="mqtt")

        self.log("Initialized Tester app!")


    def state_change(self, entity, attribute, old, new, kwargs):
        """Handle manual state changes of individual enties.

        This function stores states that were manually changed over
        the UI in the overlay scene, which has priority over all other
        scenes. We're not rendering at the end of this function, as
        the new state is already realized.

        Checking the user_id in the context of the new state allows to
        distinguish script-triggered state changes from those coming
        directly from the UI. Here, we are only interested in the
        latter.

        """

        self.log(("state change", entity, attribute, old, new, kwargs))
        self.log(self.get_state(entity, attribute="all"))
        

    def button_press(self, event_name, data, kwargs):
        """Handle button presses.

        - remove the scene from the scene stack

        """

        self.log(("button press", event_name, data, kwargs))
        self.show()


    def show(self):
        """Send the values from the

        # walk the scene stack and pick the topmost existing value for
        # each of the lights.

        """

        self.log("show, scene_stack={}".format(self.scene_stack))

        for light, data in self.lights.items():
            if data.pop("state") == "on":
                self.turn_on(light, **data)
                self.log(f"Turning on '{light}' with data '{data}'")
            else:
                self.log(f"Turning off '{light}'")
                self.turn_off(light)
