
import hassapi as hass

class LaundryReminder(hass.Hass):

    def initialize(self):

        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')

        self.power_sensor = "sensor.washing_machine_power"
        self.timer_handle = None
        self.oldpower = 0

        self.set_wm_sensor()
        self.get_entity(self.power_sensor).listen_state(self.set_wm_sensor_cb)

        self.listen_event(self.receive_telegram_callback, 'telegram_callback')


    def set_wm_sensor_cb(self, entity, attribute, old, new, kwargs):

        self.set_wm_sensor()


    def set_wm_sensor(self):

        power = int(self.get_state(self.power_sensor))

        self.wm_state = "off"
        if power > 0:
            self.wm_state = "on"

        attributes = {
            'icon': "mdi:washing-machine",
            'friendly_name': "Washing machine",
            'power': f"Currently using {power} W"
        }

        self.set_state("sensor.washing_machine", state=self.wm_state, attributes=attributes)

        if power == 0 and self.oldpower != 0:
            if self.timer_handle is not None:
                self.cancel_timer(self.timer_handle)
            self.timer_handle = self.run_in(self.notify_wm_done, 120)

        if power > 0 and self.timer_handle is not None:
            self.cancel_timer(self.timer_handle)

        self.oldpower = power


    def notify_wm_done(self, kwargs):

        if self.get_state(self.power_sensor) == "0":
            msg_data = {
                "target": self.args["telegram_target"],
                "message": "The laundry is done!",
                "inline_keyboard": [[["Got it!", "/laundry_ack"]]],
            }
            self.call_service("telegram_bot/send_message", **msg_data)

    def receive_telegram_callback(self, event, data, kwargs):

        self.log("receive_telegram_callback", (event, data, kwargs))

        if data["data"] == "/laundry_ack":
            msg_data = {
                "target": self.args["telegram_target"],
                "chat_id": data["message"]["chat"]["id"],
                "message_id": data["message"]["message_id"],
                "message": "Laundry finished",
            }
            self.call_service("telegram_bot/edit_message", **msg_data_id)
