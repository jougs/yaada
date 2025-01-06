
from pymodbus.client import ModbusTcpClient
from pymodbus.pdu import ExceptionResponse
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
from pymodbus.exceptions import ModbusException

import hassapi as hass


class Hargassner(hass.Hass):

    def decoder(self, reg):
        return BinaryPayloadDecoder.fromRegisters(reg, Endian.BIG, wordorder=Endian.BIG)

    def get_float(self, address):
        result = self.get_register_content(address)
        return self.decoder(result.registers[0:2]).decode_32bit_float()

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

        self.client = ModbusTcpClient(self.args["hargassner_ip"])

        self.run_every(self.request_modbus_data, "now", 60)

        self.get_entity("sensor.hk_boiler_temp1").listen_state(self.check_boiler_temp)


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

        self.client.connect()

        temp_sensors = {
            "hk_outdoor_temp_avg": {
                "address": 7,
                "friendly_name": "Hargassner outdoor temperature avg",
            },
            "hk_outdoor_temp": {
                "address": 9,
                "friendly_name": "Hargassner outdoor temperature",
            },
            "hk_boiler_temp1": {
                "address": 11,
                "friendly_name": "Hargassner boiler temperature 1",
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
        }

        attrs = {
            "icon": "mdi:thermometer",
            "unit_of_measurement": "°C",
            "state_class": "measurement",
            "device_class": "temperature"
        }

        for sensor, sensor_data in temp_sensors.items():
            try:
                address = sensor_data.pop("address")
                temp = f"{self.get_float(address):.2f}"
                self.set_state(f"sensor.{sensor}", state=temp, attributes=attrs|sensor_data)
                msg = f"setting state of sensor.{sensor} to {temp}"
                self.log("request_modbus_data()", msg)
            except ModbusException:
                pass


    def check_boiler_temp(self, entity, attribute, old, new, kwargs):

        #self.log("check_boiler_temp()", (entity, attribute, old, new, kwargs))

        if float(new) < 39:
            msg_data = {
                "target": self.args["telegram_target"],
                "message": "The boiler temperature fell below 39°C. Do something!",
            }
            self.call_service("telegram_bot/send_message", **msg_data)
            self.log("check_boiler_temp()", f"Sent boiler temperature warning via Telegram")
