import hassapi as hass

class DustCollection(hass.Hass):

    blast_gates = ["Maslow", "Work bench", "Table saw", "Mitre saw"]
    topic = "blast_gate/"
    input_select = "input_select.blast_gate"

    def initialize(self):

        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')
        
        self.fire_event('service_registered', domain="input_select", service="select_option")
        self.fire_event('service_registered', domain="input_select", service="set_options")
        self.fire_event('service_registered', domain="input_select", service="select_previous")
        self.fire_event('service_registered', domain="input_select", service="select_next")

        self.set_state(self.input_select, state='Table saw ', attributes={
            'options': self.blast_gates,
            'friendly_name': 'Blast gate',
            'icon': 'mdi:valve'
        })
        self.listen_event(self.select_input, **{
            'event': 'call_service',
            'domain': 'input_select',
            'service': 'select_option',
            'entity': self.input_select
        })


    def select_input(self, event_name, data, kwargs):

        if data["service_data"]["entity_id"] != self.input_select:
            return

        msg = f'event_name={event_name}, data={data}, kwargs={kwargs}'
        self.log('select_input()', msg)

        active_gate = data["service_data"]["option"]
        for gate in self.blast_gates:
            topic = self.topic + gate.lower().replace(" ", "_")
            activation = 0.6 if gate == active_gate else -0.75
            self.log('select_input()', f"sending {activation} on topic {topic}")
            self.call_service("mqtt/publish", topic=topic, payload=str(activation))

        self.set_state(self.input_select, state=active_gate)
