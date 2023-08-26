

import hassapi as hass
from dateutil.parser import isoparse

class Power(hass.Hass):

    sensors = ["Grid consumption", "Grid return"]

    def initialize(self):

        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')

        self.notified = False

        for friendly_name in self.sensors:
            sensor = "sensor." + friendly_name.lower().replace(" ", "_")
            self.get_entity(f"{sensor}_raw").listen_state(self.update_sensor)

        self.update_all_sensors()

    def update_sensor(self, entity, attribute, old, new, kwargs):

        self.update_all_sensors()

    def update_all_sensors(self):
        """Mirror values from the raw sensors to the clean ones

        The main purpose of this function is the prevention of history
        pollution. In detail, the problem prevented is like this:

        In case of a power outage, the meter is apparently reset to
        defaults, and its INFO flag gets unset. In this situation, the
        value for active power is not reported at all, while the
        values for grid consumption and return have an unusably low
        resolution in units of 1/10000th of a kWh and only 2 decimals
        accuracy.

        If handed to Home Assistant unmodified, the low resolution
        values mess up the history, as that is building a running
        difference that only works if values are of the same
        magnitude.

        Due to the extremely poor resolution, we cannot meaningfully
        convert the values for grid consumption and return and instead
        report "unknown" for the time being. To resolve the situation,
        manual configuration of the meter is required and we notify
        via Telegram reporting the time the system came up and the PIN
        for the meter.

        """

        base_attrs = {
            "icon": "mdi:lightning-bolt",
            "unit_of_measurement": "kWh",
            "state_class": "total_increasing",
            "device_class": "energy"
        }

        meter_misses_info = self.get_state("sensor.active_power") in ("unknown", "unavailable")

        for friendly_name in self.sensors:
            sensor = "sensor." + friendly_name.lower().replace(" ", "_")
            entity_attrs = {"friendly_name": friendly_name}
            if meter_misses_info:
                value = "unknown"
                entity_attrs.update({"value": self.get_state(f"{sensor}_raw", attribute="state")})
            else:
                value = float(self.get_state(f"{sensor}_raw", attribute="state"))
            self.set_state(sensor, state=value, attributes=base_attrs|entity_attrs)

        if meter_misses_info and not self.notified:
            uptime = self.get_state(f"sensor.last_boot", attribute="state")
            uptime = isoparse(uptime).strftime("%H:%M on %B %-d")
            msg_data = {
                "parse_mode": "markdown",
                "title": "*Power outage detected!*",
                "target": self.args["telegram_target"],
                "message": f"It seems there was a power outage that ended at {uptime}. "
                    " Go to the basement and tell your meter it should start to report "
                    " detailed info again! The pin is _6180_.",
                "inline_keyboard": [[["Got it!", "/power_outage_ack"]]],
            }
            self.call_service("telegram_bot/send_message", **msg_data)
            self.notified = True
