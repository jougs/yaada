
import json

from copy import copy
from pathlib import Path
from random import shuffle
from collections import OrderedDict

import hassapi as hass

from ruamel.yaml import YAML
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

yaml = YAML(typ='safe')


class LightArea:

    def __init__(self, parent, data, dirs):


        for func in ("log", "get_state", "set_state", "turn_off", "turn_on"):
            setattr(self, func, getattr(parent, func))

        self.dirs = dirs

        self.area = data["area"]
        self.lights = data["all_lights_full_on"]
        self.buttons = data["buttons"]
        self.prepare_scenes(data)

        if "ambient" in self.scenes:
            parent.listen_state(self.set_ambient, 'sensor.ambient_lights', attribute='state')

        parent.listen_event(self.button_press, 'MQTT_MESSAGE', topic='input', namespace='mqtt')

        self.scene_inputs = []
        for scene_name, scene_data in self.scenes.items():
            if "replaces" not in scene_data:
                scene_data["replaces"] = []
            scene_input = self.get_scene_input(scene_name)
            self.scene_inputs.append(scene_input)
            parent.listen_state(self.scene_change, scene_input, attribute='all')
            if not scene_name.endswith("all_off"):
                state = self.get_state(scene_input)
                scene_data["state"] = state

        self.announce_scene_inputs()
        self.show()


    def prepare_scenes(self, data):

        area_friendly = data['area_friendly']

        def add_auto_scene(scene_name, scene_state, scene_label, scene_lights):
            yaml_fname = self.dirs["scene_data"] / f"all_{scene_name}.yaml"
            self.scenes[f"{self.area}_all_{scene_name}"] = yaml.load(yaml_fname) | {
                "state": scene_state,
                "friendly_name": f"{area_friendly} {scene_label}",
                "lights": scene_lights,
            }

        self.scenes = OrderedDict()
        for scene in data["scenes"][::-1]:
            self.scenes[scene.pop("name")] = scene | {"state": "off"}

        if "ambient" in self.scenes:
            self.ambient_name = self.area + "_ambient"
            self.scenes[self.ambient_name] = self.scenes.pop("ambient")
            self.scenes[self.ambient_name]["friendly_name"] = f"{area_friendly} Ambient"
            if self.get_state('sensor.ambient_lights') not in (None, 'off'):
                self.scenes[self.ambient_name]["state"] = "on"
                self.turn_on(self.get_scene_input(self.ambient_name))
            else:
                self.scenes[self.ambient_name]["state"] = "off"
                self.turn_off(self.get_scene_input(self.ambient_name))

        on_lights = {light: state for light, state in self.lights.items()}
        add_auto_scene("on", "off", "100%", on_lights)

        off_lights = {light: {'state': 'off'} for light in self.lights.keys()}
        add_auto_scene("off", "on", "0%", off_lights)

        self.scenes.move_to_end(f"{self.area}_all_on", last=False)


    def get_scene_input(self, scene_name):
        return f"input_boolean.scene_{scene_name}"

    
    def announce_scene_inputs(self):

        self.scene_names = {}
        for scene_name, scene_data in self.scenes.items():
            fname = self.dirs["scene_inputs"] / f"scene_{scene_name}.yaml"
            with open(fname, 'w') as file:
                entity_id =f"scene_{scene_name}"
                file.write(f"{entity_id}:\n")
                file.write(f"  name: \"{scene_data['friendly_name']}\"\n")
                file.write(f"  icon: \"{scene_data['icon']}\"\n")
            self.scene_names["input_boolean." + entity_id] = scene_name
        self.log('announce_scene_inputs()', " ".join([
            f"input_boolean entity configurations have been (re-)written.",
            "You may want to restart Home Assistant or reload YAML files.",
        ]))


    def set_ambient(self, entity, attribute, old, new, kwargs):
        '''
        '''

        msg = f'entity={entity}, attribute={attribute}, old={old}, new={new}, kwargs={kwargs}'
        self.log('set_ambient()', msg)
        self.set_scene_state(self.ambient_name, new, True)


    def button_press(self, event_name, data, kwargs):
        """Handle buttons and wall switches.

        Button definitions in the YAML file can be of two forms. In
        the simple case, an MQTT topic is mapped to a scene, which
        will be toggled when the corresponding button is pressed. An
        example of this form might look like this:

        ```yaml
        bathroom_hallway_door_short: bathroom_main
        ```

        In addition to specifying just a scene to toggle, the second
        form enables the implementation of wall switches that turn on
        their designated scene, but also turn *off* additional scenes
        that might in a certain area. This form is useful for
        scenarios in which alternative scenes can be activated from
        within the area, that all should be switched off with a
        central switch when leaving the area. An example definition of
        such a button might look like this:

        ```yaml
        bathroom_hallway_door_short:
          turn_on: bathroom_main
          turn_off: [bathroom_main, bathroom_bright]
        ```
        """

        if (button := data['payload']) not in self.buttons:
            return

        msg = f'event_name={event_name}, data={data}, kwargs={kwargs}'
        self.log('button_press()', msg)

        a, b = "on", "off"
        toggle_map = {a:b, b:a}

        button_data = self.buttons[button]
        if isinstance(button_data, str):
            new_state = toggle_map[self.scenes[button_data]["state"]]
            self.set_scene_state(button_data, new_state, True)
            return

        if "toggle" in button_data:
            on_scenes = [s for s in button_data["toggle"] if self.scenes[s]["state"] == "on"]
            if not any(on_scenes):
                self.set_scene_state(button_data["toggle"][0], "on", True)
            else:
                scene_name = [s for s in button_data["toggle"] if s not in on_scenes][0]
                self.set_scene_state(scene_name, "on", True)
        else:
            on_scenes = [s for s in button_data["turn_off"] if self.scenes[s]["state"] == "on"]
            if any(on_scenes):
                for scene_name in on_scenes:
                    self.set_scene_state(scene_name, "off", True)
            else:
                self.set_scene_state(button_data["turn_on"], "on", True)


    def set_scene_state(self, scene_name, new_state, set_input):
        """Set a scene's state to 'on' or 'off'.

        If `set_input` is True, this function also sets the state of
        the *input_boolean*s related to the scene.

        If the scene is activated (by passing 'on') to `new_state`, this
        function also handles the scene replacements specified in the
        scene definition.

        """

        msg = f"scene_name={scene_name}, new_state={new_state}, set_input={set_input}"
        self.log("set_scene_state()", msg)

        if scene_name == self.area + '_all_off':
            for scene_input in self.scene_inputs:
                self.turn_off(scene_input)
            for scene_name, scene_data in self.scenes.items():
                if not scene_name.endswith("all_off"):
                    scene_data["state"] = "off"
            self.show()
            return

        if new_state == self.scenes[scene_name]["state"]:
            return

        self.scenes[scene_name]["state"] = new_state

        if new_state == "on":
            if set_input:
                self.turn_on(self.get_scene_input(scene_name))
            if "replaces" in self.scenes[scene_name]:
                for replaced_scene in self.scenes[scene_name]['replaces']:
                    self.scenes[replaced_scene]["state"] = "off"
                    self.turn_off(self.get_scene_input(replaced_scene))
        elif set_input:
            self.turn_off(self.get_scene_input(scene_name))

        self.show()


    def scene_change(self, entity, attribute, old, new, kwargs):
        '''Handle manual scene activations/deactivations.

        Checking the user_id in the context of the new state allows to
        distinguish script-triggered state changes from those coming
        directly from the UI. Here, we are only interested in the
        latter.
        '''

        msg = f'entity={entity}, attribute={attribute}, old={old}, new={new}, kwargs={kwargs}'
        self.log('scene_change()', msg)

        if 'context' in new and new['context']['user_id'] is None:
            self.log('scene_change()', 'skipping')
            return

        scene_name = self.scene_names[entity]
        self.set_scene_state(scene_name, new["state"], False)


    def show(self):
        '''Compose a final scene and realize it.

        Walk the scenes from front to back and pick the first existing
        value for each of the lights.
        '''
        scene_states = {k: v["state"] for k, v in self.scenes.items()}
        self.log('show()', f'scene_states={scene_states}')

        composite_scene = {}
        for light in self.lights.keys():
            for scene_name, scene_data in self.scenes.items():
                if scene_data["state"] == "on" and light in scene_data['lights']:
                    composite_scene[light] = copy(scene_data['lights'][light])
                    break

        composite_scene = list(composite_scene.items())
        shuffle(composite_scene)

        off_lights = []
        for entity_id, data in composite_scene:
            if data.pop('state') == 'on':
                self.log('show()', f'turning on {entity_id} with data={data}')
                self.turn_on("light." + entity_id, **data)
            else:
                off_lights.append(entity_id)

        for entity_id in off_lights:
            self.log('show()', f'turning off {entity_id}')
            self.turn_off("light." + entity_id)

    def lightconf_changed(self, *args, **kwargs):
        self.log("lightconf_changed", (args, kwargs))


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

        self.dirs = {
            "scene_data": Path(self.args["scene_data_dir"]),
            "scene_inputs": Path(self.args["scene_input_dir"]),
        }

        self.areas = {}

        for area in self.dirs["scene_data"].iterdir():
            self.add_area(area)

        observer = Observer()
        observer.schedule(Handler(self), self.dirs["scene_data"], recursive=True)
        observer.start()

        self.log('__init__()', 'initialized app')


    def add_area(self, area):
        auto_scene = any([x in str(area) for x in ("all_on.yaml", "all_off.yaml")])
        emacs_file = any([x in str(area) for x in ("~", "#")])
        if auto_scene or emacs_file:
            return

        self.log("Intitializing area", area)
        with open(area) as file:
            data = yaml.load(file)
            self.areas[str(area)] = LightArea(self, data, self.dirs)


class Handler(FileSystemEventHandler):
    def __init__(self, parent):
        super(Handler, self).__init__()
        self.log = parent.log
        self.add_area = parent.add_area
    def on_any_event(self, event):
        if event.is_directory:
            return None
        if event.event_type in ("created", "modified"):
            self.add_area(event.src_path)
