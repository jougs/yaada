
from pymodbus.client import ModbusTcpClient
from pymodbus.pdu import ExceptionResponse
from pymodbus.exceptions import ModbusException

import hassapi as hass


class Hargassner(hass.Hass):

    def get_float(self, address):
        result = self.get_register_content(address)
        dtype = self.client.DATATYPE.FLOAT32
        return self.client.convert_from_registers(result.registers[0:2], dtype, "big")

    def get_register_content(self, address):
        rr = self.client.read_holding_registers(address - 1, count=2)
        if rr.isError():
            raise ModbusException(f"Modbus library error: {rr}")
        if isinstance(rr, ExceptionResponse):
            raise ModbusException(f"Modbus library exception: {rr}")
        return rr


    def initialize(self):

        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')

        self.run_every(self.request_modbus_data, "now", 60)

        self.get_entity("sensor.hk_dhw_temp1").listen_state(self.check_dhw_temp)


    def request_modbus_data(self, kwargs):
        """
            87  Kesselzustand, Werte:
                0   KESSEL_INIT
                1   KESSEL_AUS
                2   ------------------------------------
                3   KESSEL_ZUENDPROBE
                4   KESSEL_ZUENDUNG
                5   KESSEL_LEISTUNGSBRAND
                6   KESSEL_GLUTERHALTUNG
                7   KESSEL_AUSBRAND
                8   ---------------------------------------
                9   KESSEL_ENTASCHUNG
                10  KESSEL_STB
                11  KESSEL_HAND
                12  KESSEL_STUECKHOLZ_NOTBETRIEB
            89  Leistung
            127 Rauchgastemperatur
            287 Pufferbefüllgrad
            293 AUP Strom
            223 Störungsnummer (letzte angezeigte Störung)
        """

        self.client = ModbusTcpClient(self.args["hargassner_ip"])
        self.client.connect()
        
        error_map = {
            0:    "None",
            27:   "Rauchgastemperatur unterschritten",
            309:  "Aschebox voll",
            313:  "Aschebox nicht in Position",
            314:  "Aschebox voll",
            344:  "Unterdruck zu gering",
            352:  "Fördermenge zu gering",
            6313: "Aschebox nicht in Position",
        }

        status_map = {
            0:  "Kessel Initialisierung",
            1:  "Kessel Aus",
            3:  "Kessel Zündprobe",
            4:  "Kessel Zündung",
            5:  "Kessel Leistungsbrand",
            6:  "Kessel Gluterhaltung",
            7:  "Kessel Ausbrand",
            9:  "Kessel Entaschung",
            10: "Kessel STB",
            11: "Kessel Hand",
            12: "Kessel Stückholz-Notbetrieb",
        }

        sensors = {
            "hk_outdoor_temp_avg": {
                "address": 7,
                "friendly_name": "Hargassner outdoor temperature avg",
            },
            "hk_outdoor_temp": {
                "address": 9,
                "friendly_name": "Hargassner outdoor temperature",
            },
            "hk_dhw_temp1": {  # domestic hot water
                "address": 11,
                "friendly_name": "Hargassner DHW temperature",
            },
            "hk_buffer_temp_top": {
                "address": 123,
                "friendly_name": "Hargassner buffer temperature top",
            },
            "hk_buffer_temp_middle": {
                "address": 255,
                "friendly_name": "Hargassner buffer temperature middle",
            },
            "hk_buffer_temp_bottom": {
                "address": 125,
                "friendly_name": "Hargassner buffer temperature bottom",
            },
#            "hk_buffer_charge_level": {
#                "address": 287,
#                "friendly_name": "Hargassner buffer charge level",
#                # How to remove temp_attrs? This is percentage
#            },
            "hk_last_error": {
                "address": 223,
                "friendly_name": "Hargassner last error",
                "lookup": error_map,
            },
            "hk_boiler_status": {
                "address": 87,
                "friendly_name": "Hargassner boiler status",
                "lookup": status_map,
            },
            "hk_boiler_power": {
                "address": 89,
                "friendly_name": "Hargassner boiler power",
                "as_is": True,
            },
        }

        temp_attrs = {
            "icon": "mdi:thermometer",
            "unit_of_measurement": "°C",
            "state_class": "measurement",
            "device_class": "temperature"
        }

        for sensor, sensor_data in sensors.items():
            try:
                address = sensor_data.pop("address")
                data = self.get_float(address)
                if "lookup" in sensor_data:
                    state = sensor_data.pop("lookup")[int(data)]  # might raise if error not in map
                    self.set_state(f"sensor.{sensor}", state=state, attributes=sensor_data)
                elif "as_is" in sensor_data and sensor_data.pop("as_is"):
                    self.set_state(f"sensor.{sensor}", state=f"{data:.2f}", attributes=sensor_data)
                else:
                    data = f"{data:.2f}"
                    self.set_state(f"sensor.{sensor}", state=data, attributes=temp_attrs|sensor_data)
                #self.log("request_modbus_data()", f"setting state of sensor.{sensor} to {data}")
            except ModbusException as e:
                pass #  self.log("request_modbus_data() ModbusException", e)                
            except Exception as e:
                self.log("request_modbus_data() Exception", e)


    def check_dhw_temp(self, entity, attribute, old, new, kwargs):

        if float(new) < (temp := 37):
            self.call_service(
                "telegram_bot/send_message",
                message=fr"🌡️ The DHW temperature fell below {temp}°C\!",
                chat_id=self.args["telegram_target"],
                parse_mode="markdownv2",
            )
            self.log("check_dhw_temp()", f"Sent DHW temperature warning at {temp}°C via Telegram")
