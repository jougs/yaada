from copy import copy
from datetime import datetime, timedelta
import hassapi as hass

class MotionLights(hass.Hass):

    sensors = {
        'binary_sensor.pantry_motion': {
            'delay': 5,
            'transition_on': 1,
            'transition_off': 15,
            'states': {
                "light.pantry_shelf": {"state": "on", "brightness": 255},
                "light.pantry_downlight": {"state": "on", "brightness": 255},
            }
        }
    }

    
    def initialize(self):
 
        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')

        for sensor, data in self.sensors.items():
            data["old_states"] = {}
            data["turn_off_time"] = None
            self.listen_state(self.motion_detected, sensor)

        self.run_every(self.revert_state, datetime.now(), 1)


    def motion_detected(self, trigger, attribute, old, new, kwargs):
        '''Callback for if motion was detected.

        '''

        msg = f'trigger={trigger}, attribute={attribute}, old={old}, new={new}, kwargs={kwargs}\n\n\n'
        self.log('motion_detected()', msg)

        data = self.sensors[trigger]

        for entity, state in data['states'].items():
            if data['turn_off_time'] is None:
                old_state = self.get_state(entity, attribute="all")
                keys = ('brightness',)
                attributes = old_state["attributes"] 
                data['old_states'][entity] = {k: attributes[k] for k in keys if k in attributes}
                data['old_states'][entity]['state'] = old_state["state"]
            self.set_light_state(entity, state, data["transition_on"])

        turn_off_time = datetime.now() + timedelta(seconds=data['delay'])
        self.log('motion_detected()', f'setting turn_off_time={turn_off_time} for sensor={trigger}')
        data['turn_off_time'] = turn_off_time


    def revert_state(self, kwargs):

        #self.log('revert_state()', f'kwargs={kwargs}')

        for data in self.sensors.values():
            if data["turn_off_time"] is not None and datetime.now() >= data["turn_off_time"]:
                for entity, state in data['old_states'].items():
                    self.set_light_state(entity, state, data['transition_off'])
                data["old_states"] = {}
                data["turn_off_time"] = None


    def set_light_state(self, entity, state, transition):

        self.log('set_light_state()', f'{entity}')

        data = copy(state)
        if data.pop('state') == 'on':
            data['transition'] = transition
            self.log('set_light_state()', f'turning on {entity} with data={data}')
            self.turn_on(entity, **data)
        else:
            self.log('set_light_state()', f'turning off {entity}')
            self.turn_off(entity, transition=transition)
