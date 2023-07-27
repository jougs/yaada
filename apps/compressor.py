import hassapi as hass


class Compressor(hass.Hass):
    

    def initialize(self):

        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')
        
        self.listen_event(self.button_press, 'MQTT_MESSAGE', topic='input', namespace='mqtt')


    def button_press(self, event_name, data, kwargs):

        if data['payload'] != "furnace_room_compressor_short":
            return

        self.log("button_press", "Turning compressor on")
        self.turn_on("switch.furnace_room_compressor")
        self.run_in(self.compressor_off, 60*60)

        
    def compressor_off(self, kwargs):

        self.log("compressor_off", "Turning compressor off")
        self.turn_off("switch.furnace_room_compressor")
