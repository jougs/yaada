import json
from copy import copy
import hassapi as hass
from random import shuffle


class SceneManager(hass.Hass):


    def initialize(self):
        '''Initialize the App

        This function is run upon a restart of AppDaemon or Home
        Assistant. Its main task is to register listerners for manual
        state changes, (zigbee) button presses and changes in the
        scene selection.

        Upon a restart of Home Assistant, this function will
        reconstruct the scene stack correctly, however with the
        limitation of loosing the ordering of scenes in the stack.

        '''

        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')

        self.scenes['full'] = {light: state for light, state in self.lights.items()}
        self.scenes['all_off'] = {light: {'state': 'off'} for light in self.lights.keys()}
        self.scene_stack = ['all_off']

        self.listen_state(self.set_ambient, 'sensor.ambient_lights', attribute='state')
        if self.get_state('sensor.ambient_lights') not in (None, 'off'):
            self.scene_stack.insert(1, 'ambient')

        for button in self.buttons:
            self.listen_event(self.button_press, 'MQTT_MESSAGE', topic=button, namespace='mqtt')

        for button in self.zigbee_buttons:
            self.listen_event(self.zigbee_button_press, 'MQTT_MESSAGE', topic=button, namespace='mqtt')

        self.scene_inputs = []
        for scene_input in self.scene_input_names:
            self.scene_inputs.append(self.scene_input_prefix + scene_input)

        for scene_input in self.scene_inputs:
            self.listen_state(self.scene_change, scene_input, attribute='state')
            if self.get_state(scene_input) == 'on':
                self.scene_stack.append(scene_input.split('_')[-1])

        self.show()

        self.log('__init__()', 'initialized app')


    def set_ambient(self, entity, attribute, old, new, kwargs):
        '''
        '''

        new = self.get_state(entity, attribute='all')
        msg = f'entity={entity}, attribute={attribute}, old={old}, new={new}, kwargs={kwargs}'
        self.log('set_ambient()', msg)

        if new['state'] == 'on' and 'ambient' not in self.scene_stack:
            self.scene_stack.insert(1, 'ambient')

        if 'ambient' in self.scene_stack and new['state'] == 'off':
            self.scene_stack.remove('ambient')

        self.show()


    def zigbee_button_press(self, event_name, data, kwargs):
        '''
        '''

        msg = f'event_name={event_name}, data={data}, kwargs={kwargs}'
        self.log('zigbee_button_press()', msg)

        # TODO: Make real!
        data = {
            'topic': 'input/living_chimney_left',
            'payload': json.dumps({'duration': 'short'}),
        }
        self.button_press(event_name, data, kwargs)


    def button_press(self, event_name, data, kwargs):
        '''Handle button presses.

        - remove the scene from the scene stack

        '''

        msg = f'event_name={event_name}, data={data}, kwargs={kwargs}'
        self.log('button_press()', msg)

        if data['payload'] != "ON":
            return

        press_duration = "short"

        if press_duration in ('long', 'superlong'):
            for scene_input in self.scene_inputs:
                if self.get_state(scene_input) == 'on':
                   self.turn_off(scene_input)
            self.scene_stack = ['all_off']

        if press_duration == 'short':
            scene_name = self.buttons[data['topic']]
            scene_input = self.scene_input_prefix + scene_name
            if scene_name not in self.scene_stack:
                self.scene_stack.append(scene_name)
                if scene_input in self.scene_inputs:
                    self.turn_on(scene_input)
            else:
                self.scene_stack.remove(scene_name)
                if scene_input in self.scene_inputs:
                    self.turn_off(scene_input)

        self.show()


    def scene_change(self, entity, attribute, old, new, kwargs):
        '''Handle manual scene activations/deactivations.

        Checking the user_id in the context of the new state allows to
        distinguish script-triggered state changes from those coming
        directly from the UI. Here, we are only interested in the
        latter.

        '''

        new = self.get_state(entity, attribute='all')
        msg = f'entity={entity}, attribute={attribute}, old={old}, new={new}, kwargs={kwargs}'
        self.log('scene_change()', msg)

        if new['context']['user_id'] is None:
            self.log('scene_change()', 'skipping')
            return

        scene_name = entity.split('_')[-1]
        if new['state'] == 'on' and scene_name not in self.scene_stack:
            self.scene_stack.append(scene_name)

        if new['state'] == 'off':
            self.scene_stack.remove(scene_name)

        self.show()


    def show(self):
        '''Send the values from the

        # walk the scene stack and pick the topmost existing value for
        # each of the lights.

        '''

        self.log('show()', f'scene_stack={self.scene_stack}')

        composite_scene = {}
        for light in self.lights.keys():
            for scene_name in self.scene_stack[::-1]:
                if light in self.scenes[scene_name]:
                    composite_scene[light] = copy(self.scenes[scene_name][light])
                    break

        composite_scene = list(composite_scene.items())
        shuffle(composite_scene)

        for entity_id, data in composite_scene:
            if data.pop('state') == 'on':
                self.log('show()', f'turning on {entity_id} with data={data}')
                self.turn_on(entity_id, **data)
            else:
                self.log('show()', f'turning off {entity_id}')
                self.turn_off(entity_id)
