import hassapi as hass
from requests import get
import json

from datetime import datetime, timedelta


class Calendars(hass.Hass):

    garbage_types = {
        "trash": {
            "friendly_name": "Residual and bio waste",
            "search": "Restm\xFCll",
            "icon": "mdi:delete",
        },
        "paper": {
            "friendly_name": "Paper waste",
            "search": "Papiertonne",
            "icon": "mdi:package-variant",
        },
        "recycling": {
            "friendly_name": "Recycling waste",
            "search": "Gelber Sack",
            "icon": "mdi:recycle",
        },
    }
    

    def initialize(self):

        self_log = self.log
        self.log = lambda func, msg: self_log(f'{func}: {msg}')

        self.update({})
        self.run_daily(self.update, "00:00:30")


    def update(self, kwargs):

        calendar = "calendar.m4"
        token = self.config["plugins"]["HASS"]["token"]
        ha_url = self.config["plugins"]["HASS"]["ha_url"]

        self.last_update = datetime.now()
        start_date = self.last_update.strftime("%Y-%m-%dT00:00:00")
        end_date = (self.last_update + timedelta(weeks=+5)).strftime("%Y-%m-%dT00:00:00")
        
        headers = {'Authorization': f"Bearer {token}", "content-type": "application/json"}
        apiurl = f"{ha_url}/api/calendars/{calendar}?start={start_date}Z&end={end_date}Z"

        request = get(apiurl, headers=headers, verify=False)
        self.calendar = json.loads(request.text)

        self.process_away()
        self.process_guests()
        self.process_trash()
        self.process_watering()
        

    def notify(self, msg, kb=None):

        msg_data = {
            "target": self.args["telegram_target"],
            "message": msg
        }
        if kb is not None:
            msg_data["inline_keyboard"] = kb
            
        self.call_service("telegram_bot/send_message", **msg_data)

        
    def process_away(self):
        pass

    
    def process_guests(self):
        pass

    
    def process_trash(self):

        for garbage_type, garbage_data in self.garbage_types.items():
            for entry in self.calendar:
                if entry["summary"] == garbage_data["search"]:
                    delta = datetime.strptime(entry["start"]["date"], "%Y-%m-%d") - self.last_update
                    if delta.days == 0:
                        when = "Today"
                    elif delta.days == 1:
                        self.notify(garbage_data["friendly_name"] + " pickup is tomorrow!")
                        when = "Tomorrow"
                    else:
                        when = f"Pickup in {delta.days + 1} days"

                    attributes = {k: garbage_data[k] for k in ("friendly_name", "icon")}
                    attributes["date"] = entry["start"]["date"]
                    self.set_state(f"sensor.{garbage_type}_pickup", state=when, attributes=attributes)
                    self.log("process_trashpickup", f"Setting sensor.{garbage_type}_pickup to {when}")
                    break


    def process_watering(self):

        when = "Friday"

        weekday = datetime.now().weekday()
        if weekday in [4, 5, 6]:
            when = "Today"
        elif weekday == 3:
            when = "Tomorrow"

        attributes = {"friendly_name": "Water flowers", "icon": "mdi:flower"}
        self.set_state("sensor.watering_indoor", state=when, attributes=attributes)
        self.log("process_watering", f"Setting sensor.watering_indoor to {when}")
