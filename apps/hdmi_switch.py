
import hassapi as hass


class HDMISwitch(hass.Hass):

    switches = [
        "living_room",
    ]

    def initialize(self):

        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')

        for switch in self.switches:
            # TOTO: Somehow, I thought that knowing all possible
            # values would be a good thing here. Why?
            #switch_entity = "select." + switch + "_hdmi_switch"
            #self.log("initialize()", self.get_state(switch_entity))

            self.listen_event(self.set_hdmi_switch, 'MQTT_MESSAGE', topic="hdmi_switch/" + switch, namespace='mqtt')

        
    def set_hdmi_switch(self, event_name, data, kwargs):

        msg = f'event_name={event_name}, data={data}, kwargs={kwargs}'
        self.log('set_hdmi_switch()', msg)

        switch_entity = "select." + data['topic'].split('/')[1] + "_hdmi_switch"
        self.set_state(switch_entity, state=data["payload"])
