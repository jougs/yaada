
import time
import random

import hassapi as hass
from datetime import datetime, timedelta

evc_pmin, evc_pmax = 5000, 12000  # solar production range in W for solar only charging
evc_cmin, evc_cmax = 6, 16        # charging current range in A per phase

def ev_charging_current(prod):
    cc = evc_cmin + (prod - evc_pmin) * (evc_cmax - evc_cmin) / (evc_pmax - evc_pmin)
    return min(evc_cmax, int(cc))


class HEMS(hass.Hass):

    num_el_on_old = 0

    def initialize(self):

        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')

        ev_charge_mode_select = "select.utility_wing_ev_charger_ev_charge_mode"
        self.listen_state(self.ev_charge_mode_selected, ev_charge_mode_select)
        self.ev_charge_mode = self.get_state(ev_charge_mode_select)

        self.run_every(self.handle_ev_charging, "now", 30)

        now_plus_15s = datetime.now() + timedelta(seconds=15)
        self.run_every(self.handle_immersion_heater, now_plus_15s, 30)


    def ev_charge_mode_selected(self, entity, attribute, old, new, kwargs):

        self.ev_charge_mode = new
        self.manage_energy({})
        self.log("ev_charge_mode_selected", self.ev_charge_mode)


    def handle_ev_charging(self, kwargs):

        car_soc = float(self.get_state("sensor.i3_120_battery_ev_state_of_charge"))

        turn_func = self.turn_off
        current = 6

        if "Grid slow" == self.ev_charge_mode and car_soc < 95:
            turn_func, current = self.turn_on, 6

        if "Grid fast" == self.ev_charge_mode:
            turn_func, current = self.turn_on, 16

        if "Solar only" == self.ev_charge_mode and car_soc < 95:
            production = float(self.get_state("sensor.pv_production_now"))
            active_power = float(self.get_state("sensor.basement_tech_room_io_active_power"))
            if production > 5000 and active_power < -250:
                turn_func, current = self.turn_on, ev_charging_current(production)

        turn_func("switch.garage_ev_charger_enable")
        self.set_state("number.garage_ev_charger_max_amps", state=current)


    def handle_immersion_heater(self, kwargs):

        active_power = float(self.get_state("sensor.basement_tech_room_io_active_power"))
        if active_power > -250:
            return
        
        usable_power = -active_power + self.num_el_on_old * 2750
        if (num_el_on := min(int(usable_power / 2750), 3)) == self.num_el_on_old:
            return

        temp = self.get_state("sensor.hk_buffer_temp_middle")
        if temp is None or temp in ["unavailable", "unknown"]:
            return
        
        if float(temp) >= 75:
            num_el_on = 0

        el_on = random.sample(range(3), num_el_on)
        func = getattr(self, f"turn_{'on' if el_on else 'off'}")

        if el_on:
            self.log("immersion_heater()", (el_on, usable_power, active_power))

#        for el in el_on or range(3):
#            func(f"switch.furnace_room_light_buffer_immersion_heater_{el + 1}")

        self.num_el_on_old = num_el_on
