
import hassapi as hass
from collections import deque

class BathroomFan(hass.Hass):

    def initialize(self):

        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')

        self.sensor_name = "sensor.uponor_masterbad_humidity"

        self.humidity_stats = deque([], 15)
        self.humidity_mean = 100
        self.old_humidity = self.humidity_mean
        self.auto_on_humidity = None
        self.timer = None
        
        self.run_every(self.update_humidity_stats, "now", 60)
        self.get_entity(self.sensor_name).listen_state(self.humidity_changed)
        

    def update_humidity_stats(self, kwargs):

        humidity = self.get_state(self.sensor_name)
        try:
            self.humidity_stats.append(float(humidity))
            self.humidity_mean = sum(self.humidity_stats)/len(self.humidity_stats)
        except:
            pass

        msg = f"Mean humidity over the last {len(self.humidity_stats)} minutes: {self.humidity_mean}"
        self.log("update_humidity_stats()", msg)
        

    def humidity_changed(self, entity, attribute, old, new, kwargs):

        self.log("humidity_changed()", (entity, attribute, old, new, kwargs))
        humidity = float(new)

        if self.auto_on_humidity is None and humidity > self.humidity_mean * 1.13:
            if self.timer is not None:
                self.cancel_timer(self.timer)
            self.turn_on("fan.bathroom_fan")
            self.auto_on_humidity = self.humidity_mean
            self.log("check_humidity()", f"Turning fan on, humidity is {humidity}")
            
        if self.auto_on_humidity is not None and humidity < self.auto_on_humidity * 1.12:
            if self.timer is not None:
                self.cancel_timer(self.timer)
            self.timer = self.run_in(self.turn_fan_off, 5*60, humidity=humidity)

        self.old_humidity = humidity

        
    def turn_fan_off(self, kwargs):
        self.log("turn_fan_off()", f"Turning fan off, humidity is {kwargs['humidity']}")
        self.turn_off("fan.bathroom_fan")
        self.auto_on_humidity = None
        self.timer = None
