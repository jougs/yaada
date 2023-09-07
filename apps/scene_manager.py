import hassapi as hass
import json

from random import shuffle
from copy import copy
from os import path


class SceneManager(hass.Hass):


    def initialize(self):
        '''Initialize the App

        This function is run upon a restart of AppDaemon or Home
        Assistant. Its main task is to register listerners for manual
        state changes, wall switch button presses and changes in the
        scene selection.

        This app also respects the state of sensor.ambient_lights by
        activating or deactivating the ambient light scene
        accordingly.

        When the app starts, it registers one input_boolean with Home
        Assistant using MQTT discovery. The name of the input is given
        by the scene_input_prefix plus the

        Upon a restart of Home Assistant, this function will
        reconstruct the scene stack correctly, however with the
        limitation of loosing the ordering of scenes in the stack.

        '''

        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')

        self.unique_id = self.area.lower().replace(" ", "_")

        self.scenes['full'] = {
            'name': 'all on',
            'icon': 'mdi:sunglasses',
            'replaces': [],
            'lights': {light: state for light, state in self.lights.items()}
        }

        self.scenes['alloff'] = {
            'name': 'all off',
            'icon': 'mdi:lightbulb-off',
            'replaces': [],
            'lights': {light: {'state': 'off'} for light in self.lights.keys()}
        }

        self.scene_stack = ['alloff']

        self.listen_state(self.set_ambient, 'sensor.ambient_lights', attribute='state')
        if self.get_state('sensor.ambient_lights') not in (None, 'off') and "ambient" not in self.scene_stack:
            self.scene_stack.insert(1, 'ambient')
            attr = {"icon": self.scenes["ambient"]["icon"]}
            self.set_state(self.get_scene_input('ambient'), state='on', attributes=attr)

        self.listen_event(self.button_press, 'MQTT_MESSAGE', topic='input', namespace='mqtt')

        self.scene_inputs = []
        for scene_name, scene_data in self.scenes.items():
            scene_input = self.get_scene_input(scene_name)
            self.scene_inputs.append(scene_input)
            if self.get_state(scene_input) == 'on' and scene_name not in self.scene_stack:
                self.scene_stack.append(scene_name)
            self.listen_state(self.scene_change, scene_input, attribute='state')

        self.announce_scene_inputs()

        self.show()

        self.log('__init__()', 'initialized app')


    def get_scene_input(self, scene_name):
        return f"input_boolean.scene_{self.unique_id}_{scene_name}"


    def announce_scene_inputs(self):

        data_path = '/srv/homeassistant/data/entities/input_boolean'

        for scene_name, scene_data in self.scenes.items():
            fname = f"scene_{self.unique_id}_{scene_name}.yaml"
            with open(path.join(data_path, fname), 'w') as file:
                file.write(f"scene_{self.unique_id}_{scene_name}:\n")
                file.write(f"  name: {self.area} scene {scene_data['name']}\n")
                file.write(f"  icon: {scene_data['icon']}\n")
            msg = f"Configuration file {fname} has been rewritten. "
            msg += "You may want to restart Home Assistant."
            self.log('announce_scene_inputs()', msg)


    def set_ambient(self, entity, attribute, old, new, kwargs):
        '''
        '''

        new = self.get_state(entity, attribute='all')
        msg = f'entity={entity}, attribute={attribute}, old={old}, new={new}, kwargs={kwargs}'
        self.log('set_ambient()', msg)

        attr = {"icon": self.scenes["ambient"]["icon"]}

        if self.scenes["ambient"]['lights'] and new['state'] == 'on' and 'ambient' not in self.scene_stack:
            self.scene_stack.insert(1, 'ambient')
            self.set_state(self.get_scene_input('ambient'), state='on', attributes=attr)

        if 'ambient' in self.scene_stack and new['state'] == 'off':
            self.scene_stack.remove('ambient')
            self.set_state(self.get_scene_input('ambient'), state='off')

        self.show()


    def button_press(self, event_name, data, kwargs):
        '''Handle button presses.

        - remove the scene from the scene stack

        '''

        button = data['payload']
        if button not in self.buttons:
            return

        msg = f'event_name={event_name}, data={data}, kwargs={kwargs}'
        self.log('button_press()', msg)

        # TODO: check if scene is a compound and act accordingly
        # TODO: i.e. handle lists of scenes to activate and deactivate

        scene_name = self.buttons[button]
        if scene_name == 'alloff':
            for scene_input in self.scene_inputs:
                if self.get_state(scene_input) == 'on':
                    self.turn_off(scene_input)
            self.scene_stack = ['alloff']
            return

        scene_input = self.get_scene_input(scene_name)
        if scene_name not in self.scene_stack:
            self.scene_stack.append(scene_name)
            if scene_input in self.scene_inputs:
                self.turn_on(scene_input)
            for scene_name_inverse in self.scenes[scene_name]['replaces']:
                if scene_name_inverse in self.scene_stack:
                    scene_input = self.get_scene_input(scene_name_inverse)
                    self.scene_stack.remove(scene_name_inverse)
                    if scene_input in self.scene_inputs:
                        self.turn_off(scene_input)
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
            for scene_name_inverse in self.scenes[scene_name]['replaces']:
                if scene_name_inverse in self.scene_stack:
                    scene_input = self.get_scene_input(scene_name_inverse)
                    self.scene_stack.remove(scene_name_inverse)
                    if scene_input in self.scene_inputs:
                        self.turn_off(scene_input)

        if new['state'] == 'off':
            if scene_name in self.scene_stack:
                self.scene_stack.remove(scene_name)
            else:
                self.log("scene_change()", f"scene {scene_name} not in stack")

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
                if light in self.scenes[scene_name]['lights']:
                    composite_scene[light] = copy(self.scenes[scene_name]['lights'][light])
                    break

        composite_scene = list(composite_scene.items())
        shuffle(composite_scene)

        off_lights = []
        for entity_id, data in composite_scene:
            if data.pop('state') == 'on':
                self.log('show()', f'turning on {entity_id} with data={data}')
                self.turn_on(entity_id, **data)
            else:
                off_lights.append(entity_id)

        for entity_id in off_lights:
            self.log('show()', f'turning off {entity_id}')
            self.turn_off(entity_id)
