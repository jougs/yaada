
import hassapi as hass
import json
import time

class MovieLights(hass.Hass):

    kb_lights = {
        True: ["Turn  movie lights off", "/movie_lights_off"],
        False: ["Turn movie lights on", "/movie_lights_on"],
    }

    kb_amps = {
        True: ["Turn amplifiers off", "/movie_amps_off"],
        False: ["Turn amplifiers on", "/movie_amps_on"],
    }

    kb_play = {
        True: ["Pause", "/movie_pause"],
        False: ["Play", "/movie_play"],
    }

    kb_dismiss = ["Dismiss", "/movie_dismiss"]
    
    msg_ending = {
        "ended": "has ended",
        "dismissed": "was cancelled"
    }
    
    amps = [
        "light.living_room_floor_tank_1",
        "light.living_room_wall_socket_media",
    ]

    def initialize(self):

        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')

        self.set_defaults()
        
        self.listen_event(self.receive_telegram_callback, 'telegram_callback')
        self.listen_event(self.on_playbackstate, 'MQTT_MESSAGE', topic="kodi/status/playbackstate", namespace='mqtt')
        self.listen_event(self.on_title, 'MQTT_MESSAGE', topic="kodi/status/playertitle", namespace='mqtt')        
        self.listen_event(self.on_title, 'MQTT_MESSAGE', topic="kodi/status/title", namespace='mqtt')        
        self.listen_event(self.on_telegram_sent, 'telegram_sent')

    def set_defaults(self, newstate=None):
        
        self.log("set_defaults()", newstate)
        
        self.last_event = int(time.time() * 1000)
        self.movie_lights = False
        self.movie_amps = False
        self.message_tag = ""
        
        if newstate in ("ended", "dismissed"):
            message_ending = self.msg_ending[newstate]
            msg_data = {
                "target": self.args["telegram_target"],
                "message": f"Playback of _{self.movie_title}_ {message_ending}",
                "message_id": self.message_id,
                "chat_id": self.chat_id,
            }
            self.call_service("telegram_bot/edit_message", **msg_data)
        
        if newstate == "started":
            self.playing = True
            self.message_tag = f"kodi_living_area_{time.time()}"
            if self.movie_title:
                message = f"Playback of _{self.movie_title}_ has started"
            else:
                message = f"Playback has started"
            msg_data = {
                "target": self.args["telegram_target"],
                "message_tag": self.message_tag,
                "message": message, 
                "inline_keyboard": self.get_inline_keyboard(),
            }
            self.call_service("telegram_bot/send_message", **msg_data)
            self.log("set_defaults()", "message sent: " + message)
            return

        self.message_id = None
        self.movie_title = ""
        self.playing = False
        
    def get_inline_keyboard(self):
        return [
            [self.kb_lights[self.movie_lights]],
            [self.kb_amps[self.movie_amps]],
            [self.kb_play[self.playing]],
            [self.kb_dismiss],
        ]

    def on_telegram_sent(self, event_name, data, kwargs):

        self.log("on_telegram_sent()", (event_name, data, kwargs))

        if "message_tag" in data and data["message_tag"] == self.message_tag:
            self.message_id = data["message_id"]
            self.chat_id = data["chat_id"]

    def on_title(self, event_name, data, kwargs):
            
        self.log("on_title()", data)
        self.movie_title = json.loads(data["payload"])["val"]

        if self.message_id:
            msg_data = {
                "target": self.args["telegram_target"],
                "message": f"Playback of _{self.movie_title}_ has started",
                "message_id": self.message_id,
                "chat_id": self.chat_id,
                "inline_keyboard": self.get_inline_keyboard(),
            }
            self.call_service("telegram_bot/edit_message", **msg_data)
        
        
    def on_playbackstate(self, event_name, data, kwargs):
        
        now = int(time.time() * 1000)
        time_since_last_event = now  - self.last_event
        self.last_event = now
        if time_since_last_event < 1000:
            self.log("on_playbackstate()", time_since_last_event)
            return

        self.log("on_playbackstate()", data)
        kodi_state = json.loads(data["payload"])["kodi_state"]
        
        if kodi_state == "started":
            self.set_defaults("started")

        if kodi_state == "resumed":
            self.playing = True

        if kodi_state == "ended":
            self.set_defaults("ended")

        if kodi_state in ("paused", "ended"):
            self.playing = False
            
        self.set_movie_lights_and_amps()


    def set_movie_lights_and_amps(self):

        if self.movie_lights:
            if self.playing:
                self.turn_on("input_boolean.scene_living_area_movies")
            else:
                self.turn_off("input_boolean.scene_living_area_movies")
                    
        if self.movie_amps:
            for amp in self.amps:
                self.turn_on(amp)
        else:
            for amp in self.amps:
                self.turn_off(amp)


    def receive_telegram_callback(self, event, data, kwargs):

        self.log("receive_telegram_callback", (event, data, kwargs))

        if data["data"] == "/movie_lights_on":
            self.movie_lights = True

        if data["data"] == "/movie_lights_off":
            self.movie_lights = False

        if data["data"] == "/movie_amps_on":
            self.movie_amps = True

        if data["data"] == "/movie_amps_off":
            self.movie_amps = False

        if data["data"] == "/movie_play":
            self.call_service("mqtt/publish", topic="kodi/command/playbackstate", payload='1')
            self.playing = True

        if data["data"] == "/movie_pause":
            self.call_service("mqtt/publish", topic="kodi/command/playbackstate", payload='2')
            self.playing = False

        if data["data"] == "/movie_dismiss":
            if self.playing:
                self.call_service("mqtt/publish", topic="kodi/command/playbackstate", payload='0')
            self.set_defaults("dismissed")

        self.set_movie_lights_and_amps()

        if data["data"] != "/movie_dismiss":
            msg_data = {
                "target": self.args["telegram_target"],
                "message": f"Playback of _{self.movie_title}_ has started",
                "message_id": data["message"]["message_id"],
                "chat_id": data["message"]["chat"]["id"],
                "inline_keyboard": self.get_inline_keyboard(),
            }
            self.call_service("telegram_bot/edit_message", **msg_data)
