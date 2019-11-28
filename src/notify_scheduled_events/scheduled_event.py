import re
import botocore.errorfactory
import datetime
import html.entities
from typing import List, Dict
from googleapiclient.discovery import build


class GoogleCalendarAPI:
    def __init__(self, api_key: str, tz: datetime.timezone):
        self._service = build('calendar', 'v3', developerKey=api_key, cache_discovery=False)
        self._timezone = tz

    def get_items(self, calendar_id: str, start: datetime.datetime, end: datetime.datetime, max_results: int) -> List[dict]:
        res = self._service.events().list(
            calendarId=calendar_id,
            timeMin=start.astimezone(self._timezone).isoformat(),
            timeMax=end.astimezone(self._timezone).isoformat(),
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return res.get('items', [])

    @property
    def timezone(self):
        return self._timezone


class ScheduledEvent:
    def __init__(self, item_id: str, title: str, description: str, start: datetime.datetime, notify_needed: bool):
        self._item_id = item_id
        self._title = title
        self._description = description
        self._start = start
        self._notify_needed = notify_needed

    @property
    def dictionary(self) -> dict:
        return {
            'id': self._item_id,
            'title': self._title,
            'description': self.description,
            'y': self._start.year,
            'm': self._start.month,
            'd': self._start.day,
            'H': self._start.hour,
            'MM': '{0:02}'.format(self._start.minute),
            'notify_needed': self._notify_needed,
        }

    @property
    def item_id(self) -> str:
        return self._item_id

    @property
    def notify_needed(self) -> bool:
        return self._notify_needed

    @property
    def description(self) -> str:
        s = re.compile(r"<[^>]*?>")
        res = s.sub("", self._description)
        for i in re.findall('&[a-zA-Z]+?;', res):
            try:
                r = html.entities.name2codepoint[i[1:-1]]
                res = res.replace(i, chr(r))
            except KeyError:
                continue
        return res


class ScheduledEventsRepository:
    def __init__(self, s3, cache_bucket_name: str, api: GoogleCalendarAPI, calendar_id: str):
        self._cache: Dict[str, str] = {}
        self._s3 = s3
        self._bucket = cache_bucket_name
        self._api = api
        self._calendar_id = calendar_id

    def get_events(self, start: datetime.datetime, end: datetime.datetime) -> List[ScheduledEvent]:
        events = self._api.get_items(self._calendar_id, start, end, 10)
        res = []
        for e in events:
            s = datetime.datetime.strptime(e['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z').astimezone(self._api.timezone)
            try:
                item_id = e['id']
                res.append(ScheduledEvent(
                    item_id=item_id,
                    title=e.get('summary', ''),
                    description=e.get('description', ''),
                    start=s,
                    notify_needed=self._notify_needed(item_id)
                ))
            except KeyError:
                continue
        return res

    def mark_as_notified(self, item_id: str):
        self._s3.put_object(Bucket=self._bucket, Key='{0}/{1}'.format(self._calendar_id, item_id), Body='')

    def _notify_needed(self, item_id: str):
        try:
            self._s3.head_object(Bucket=self._bucket, Key='{0}/{1}'.format(self._calendar_id, item_id))
            return False
        except botocore.errorfactory.ClientError:
            return True
