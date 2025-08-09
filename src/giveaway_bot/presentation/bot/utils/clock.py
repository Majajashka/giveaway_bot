from datetime import datetime

import pytz


class LocalizedClock:

    def __init__(self, timezone: str):
        self._timezone = timezone

    def now(self) -> datetime:
        local_tz = pytz.timezone(self._timezone)
        return datetime.now(local_tz).replace(tzinfo=None)

    def convert_utc_to_local(self, utc_dt: datetime) -> datetime:
        local_tz = pytz.timezone(self._timezone)
        return utc_dt.astimezone(local_tz)

    def parse_local_time_as_utc(self, time_str: str, template: str = "%d-%m-%Y %H:%M") -> datetime:
        local_tz = pytz.timezone(self._timezone)
        naive_dt = datetime.strptime(time_str, template)
        local_dt = local_tz.localize(naive_dt)
        return local_dt.astimezone(pytz.utc).replace(tzinfo=None)

    def parse_utc_time(self, time_str: str, template: str = "%d-%m-%Y %H:%M:%S") -> datetime:
        utc_tz = pytz.utc
        naive_dt = datetime.strptime(time_str, template)
        utc_dt = utc_tz.localize(naive_dt)
        return utc_dt.replace(tzinfo=None)
