
import hassapi as hass


class Solar(hass.Hass):

    prefix = "sensor.growatt_shinewifi_x_"

    solar_sensors = [
        "energy_today",
        "energy_total",
        "ac1_power",
        "ac2_power",
        "ac3_power",
        "pv1_dc_voltage",
        "pv1_dc_current",
        "pv2_dc_voltage",
        "pv2_dc_current",
    ]

    def initialize(self):

        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')

        for sensor in self.solar_sensors:
            self.get_entity(self.prefix + sensor).listen_state(self.update_sensor)

        self.get_entity("sensor.active_power").listen_state(self.update_house_meter_sensors)
            
        self.update_house_meter_sensors(0,0,0,0,0)
        self.update_all_sensors()
        

    def update_sensor(self, entity, attribute, old, new, kwargs):

        self.update_all_sensors()


    def set_sensor(self, entity, friendly_name, icon, unit, zero_by_night, *sensors):

        values = []
        for sensor in sensors:
            values.append(self.get_state(self.prefix + sensor))

        state = None
        try:
            [float(v) for v in values]
            state = "/".join(values) + " " + unit
        except ValueError:
            if zero_by_night:
                state = "/".join(["0.0"] * len(values)) + " " + unit

        if state is not None:
            attributes = {"friendly_name": friendly_name, "icon": icon}
            self.set_state(f"sensor.{entity}", state=state, attributes=attributes)


    def update_all_sensors(self):

        self.set_sensor("pv_dc_current", "Current string 1/2", "mdi:current-dc", "A", True, "pv1_dc_current", "pv2_dc_current")
        self.set_sensor("pv_dc_power", "Power string 1/2", "mdi:flash", "W", True, "pv1_dc_power", "pv2_dc_power")
        self.set_sensor("pv_dc_voltage", "Voltage string 1/2", "mdi:sine-wave", "V", True, "pv1_dc_voltage", "pv2_dc_voltage")

        self.set_sensor("pv_ac_current", "Current phase 1/2/3", "mdi:current-ac", "A", True, "ac1_current", "ac2_current", "ac3_current")
        self.set_sensor("pv_ac_power", "Power phase 1/2/3", "mdi:flash", "W", True, "ac1_power", "ac2_power", "ac3_power")
        self.set_sensor("pv_ac_voltage", "Voltage phase 1/2/3", "mdi:sine-wave", "V", True, "ac1_voltage", "ac2_voltage", "ac3_voltage")

        self.set_sensor("pv_production", "Production today/total", "mdi:solar-power", "kWh", False, "energy_today", "energy_total")

        dc_power = [self.get_state(self.prefix + entity) for entity in ("pv1_dc_power", "pv2_dc_power")]
        if 'unavailable' not in dc_power:
            dc_power = sum(map(lambda x: float(x), dc_power))
            if dc_power != 0:
                efficiency = (float(self.get_state(self.prefix + "ac_power")) / dc_power) * 100
                if efficiency <= 100:
                    attributes = {"friendly_name": "Conversion efficiency", "icon": "mdi:cog-clockwise", "unit_of_measurement": " %"}
                    self.set_state("sensor.pv_efficiency", state=f"{efficiency:.2f}", attributes=attributes)
        
                peak_percentage = (dc_power / 12000) * 100
                attributes = {"friendly_name": "Peak percentage", "icon": "mdi:chart-donut", "unit_of_measurement": " %"}
                self.set_state("sensor.pv_peak_percentage", state=f"{peak_percentage:.2f}", attributes=attributes)
            
        pv_status = self.get_state("sensor.growatt_shinewifi_x_status")
        pv_status = pv_status if pv_status != "unavailable" else "Offline"
        attributes = {"friendly_name": "Inverter status", "icon": "mdi:heart-pulse"}
        self.set_state(f"sensor.pv_status", state=pv_status, attributes=attributes)


    def update_house_meter_sensors(self, entity, attribute, old, new, kwargs):

        ac_power = self.get_state(self.prefix + "ac_power")
        ac_power = float(ac_power) if ac_power != 'unavailable' else 0
        active_power = self.get_state("sensor.active_power")
        house_power_consumption = "unavailable" if active_power in ("unavailable", "unknown") else int(ac_power + float(active_power))

        attributes = {"friendly_name": "House power consumption", "icon": "mdi:flash", "unit_of_measurement": "W", "state_class": "measurement", "device_class": "energy"}
        self.set_state("sensor.house_power_consumption", state=f"{house_power_consumption}", attributes=attributes)
        
