from copy import copy
from random import shuffle
import hassapi as hass
import json

start_time = "sunset - 00:30:00"
end_time = "02:00:00"

class AmbientLights(hass.Hass):

    sensor = "sensor.ambient_lights"
    attributes = {"friendly_name": "Ambient Lights"}

    def initialize(self):
        """Initialize the App

        This function is run upon a restart of AppDaemon or Home
        Assistant. Its only task is to set the state of the sensor
        ambient_lights to "on" or "off".

        Upon a restart of Home Assistant, this function will set the
        state correctly, but apps relying on the value of the sensor
        should nonetheless be prepared for a temporary unavailability
        of the sensor. The following construct can be used for added
        safety:

            state = self.get_state("sensor.ambient_lights")
            ambient_lights_on = state not in (None, "off")

        """

        on = lambda kwargs: self.set_ambient_lights("on", kwargs)
        off = lambda kwargs: self.set_ambient_lights("off", kwargs)

        if self.now_is_between(start_time, end_time):
            on({})
        else:
            off({})

        self.run_daily(on, start_time)
        self.run_daily(off, end_time)


    def set_ambient_lights(self, state, kwargs):

        self.log("setting ambient lights to '{}', kwargs={}".format(state, kwargs))

        self.set_state(self.sensor, state=state, attributes=self.attributes)
