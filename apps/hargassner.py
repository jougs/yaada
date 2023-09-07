
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
            raise ModbusException("Modbus library error: {rr}")
        if isinstance(rr, ExceptionResponse):
            raise ModbusException(f"Modbus library exception: {rr}")
        return rr

    
    def initialize(self):
        
        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')

        self.client = ModbusTcpClient(self.args["hargassner_ip"])
        
        self.run_every(self.run_every_five_min, "now", 5 * 60)

        
    def run_every_five_min(self, kwargs):

        self.client.connect()

        #   7 Außentemperatur gemittelt
        #   9 Außentemperatur aktuell
        #  11 Boilertemperatur 1
        # 123 Puffertemperatur Oben
        # 255 Puffertemperatur Mitte
        # 125 Puffertemperatur Unten
        
        temp_sensors = {
            "hk_outdoor_temp": {"friendly_name": "Hargassner outdoor temperature", "address": 9},
            #"hk_boiler_temp1": {"friendly_name": "Hargassner boiler temperature 1", "address": 11},
            #"hk_buffer_temp_top": {"friendly_name": "Hargassner buffer temperature top", "address": 123},
            #"hk_buffer_temp_middle": {"friendly_name": "Hargassner buffer temperature middle", "address": 255},
            #"hk_buffer_temp_bottom": {"friendly_name": "Hargassner buffer temperature bottom", "address": 125},
        }

        for sensor, sensor_data in temp_sensors.items():
            try:
                address = sensor_data.pop("address")
                attrs = {"icon": "mdi:thermometer", "unit_of_measurement": "°C", "state_class": "measurement", "device_class": "temperature"}
                temperature = self.get_float(address)
                self.set_state(f"sensor.{sensor}", state=f"{temperature:.2f}", attributes=attrs|sensor_data)
                self.log("run_every_five_min", f"setting state of sensor.{sensor} to {temperature:.2f}")
            except ModbusException:
                pass
        
        # 287 Pufferbefüllgrad

        #"hk_buffer_level": {"friendly_name": "Hargassner buffer level", "address": 287, unit_of_measurement": "%"},            
            
        # 293 AUP Strom
        # 223 Störungsnummer (letzte angezeigte Störung)
        # 87  Kesselzustand
        # 89  Leistung
        # 127 Rauchgastemperatur
        # 
        # Werte 87:
        # 0   KESSEL_INIT
        # 1   KESSEL_AUS
        # 2   ------------------------------------
        # 3   KESSEL_ZUENDPROBE
        # 4   KESSEL_ZUENDUNG
        # 5   KESSEL_LEISTUNGSBRAND
        # 6   KESSEL_GLUTERHALTUNG
        # 7   KESSEL_AUSBRAND
        # 8   ---------------------------------------
        # 9   KESSEL_ENTASCHUNG
        # 10  KESSEL_STB
        # 11  KESSEL_HAND
        # 12  KESSEL_STUECKHOLZ_NOTBETRIEB














