
import json
import hassapi as hass
from copy import copy
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from time import sleep


class Mediabox(hass.Hass):

    mediaboxes = {
        "living_room_mediabox": {
            "name": "Living room Spotify",
            "amps" : [
                "light.living_room_floor_tank_1",
                "light.living_room_wall_socket_media",
            ],
            "delay": 0,
            "hdmi_switch": {
                "topic": "living_room_hdmi_switch/command",
                "payload": "Media center",
            },
        },
        "mancave_musicbox": {
            "name": "Mancave Spotify",
            "amps" : [
                "switch.mancave_pa_mixer",
                "switch.mancave_pa_amplifier_1",
                "switch.mancave_pa_amplifier_2",
            ],
            "delay": 1.5,
        },
        "bedroom_musicbox": {
            "name": "Bedroom Spotify",
            "amps" : [
                "light.master_bedroom_tube_radio",
            ],
            "delay": 0,
        },
        "office_musicbox": {
            "name": "Office Spotify",
            "amps" : [],
            "delay": 0,
        },
    }


    def initialize(self):

        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')

        self.spotify = Spotify(client_credentials_manager=SpotifyClientCredentials())

        for topic, mediabox in self.mediaboxes.items():
            self.listen_event(self.state_change, 'MQTT_MESSAGE', topic=topic+"/status", namespace='mqtt')

            sensor_name = "sensor." + mediabox["name"].lower().replace(" ", "_")
            mediabox["sensor_name"] = sensor_name

            attributes = {'icon': "mdi:stop", 'friendly_name': mediabox["name"]}
            self.set_state(sensor_name , state="Not connected", attributes=attributes)



    def state_change(self, event_name, data, kwargs):

        msg = f'event_name={event_name}, data={data}, kwargs={kwargs}'
        self.log('state_change()', msg)

        mediabox = data['topic'].split('/')[0]
        if mediabox not in self.mediaboxes:
            return

        payload = json.loads(data['payload'])
        self.log('state_change()', f"payload={payload}")

        state = None # Don't do anything for events change and volume_set

        if payload['event'] == 'paused':
            state = {
                "icon": "mdi:pause",
                "state": "Not playing",
                "amp": "off"
            }

        if payload['event'] in ('off', 'stop', 'stopped'):
            state = {
                "icon": "mdi:stop",
                "state": "Not connected",
                "amp": "off"
            }

        if payload['event'] == 'playing':
            track_info = self.spotify.track("spotify:track:" + payload["track_id"])
            track_name = track_info["name"]
            artists = " & ".join([artist["name"] for artist in track_info["artists"]])
            album = track_info["album"]["name"]
            state = {
                "icon": "mdi:play",
                "state": f"{track_name} by {artists}",
                "amp": "on"
            }

        if payload['event'] == 'on':
            state = {
                "icon": "mdi:play",
                "state": "Manual operation",
                "amp": "on"
            }

        if state is not None:
            mediabox = self.mediaboxes[mediabox]

            if "hdmi_switch" in mediabox:
                topic = mediabox["hdmi_switch"]["topic"]
                payload = mediabox["hdmi_switch"]["payload"]
                self.call_service("mqtt/publish", topic=topic, payload=payload)

            state['friendly_name'] = mediabox['name']
            self.set_state(mediabox['sensor_name'], state=state.pop('state'), attributes=state)

            # switch amps last, as this might involve delays
            amp_state = state.pop('amp')
            amps = mediabox['amps'] if amp_state == 'on' else mediabox['amps'][::-1]
            for amp in amps:
                # TODO: Leave on if
                #  * Kodi is currently playing and has requested the amp to be on
                #  * Spotify's last status change was to playing
                #  * the source selector is set on HDMI and the amp is turned on
                #  * the source selector is on external audio
                # curl -D - -H 'Content-Type: applson' -d '{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}' localhost/jsonrpc
                # curl -D - -H 'Content-Type: applson' -d '{"jsonrpc": "2.0", "method": "Player.GetProperties", "id": 1, "params": {"playerid": 1, "properties": ["speed"]}}' localhost/jsonrpc
                # id: just some sequence number to relate the response to the request
                # speed: is returned as 0 if the player is on pause

                self.set_amp_state(amp, {'state': amp_state})
                sleep(mediabox["delay"])


    def set_amp_state(self, entity, state):

        self.log('set_state()', f'{entity}')

        data = copy(state)
        if data.pop('state') == 'on':
            self.log('set_state()', f'turning on amp {entity} with data={data}')
            self.turn_on(entity, **data)
        else:
            self.log('set_state()', f'turning off amp {entity}')
            self.turn_off(entity)
