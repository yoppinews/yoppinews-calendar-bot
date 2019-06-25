# -*- coding: utf-8 -*-

import json
import string
import datetime

from logging import Logger
from typing import List
from functools import reduce


class GoogleCalendarSummarizer:
    def __init__(self, calendar_service, timezone: datetime.timezone, logger: Logger):
        self._calendar_service = calendar_service
        self._timezone = timezone
        self._logger = logger

    def summarize(self, calendar_id: str, message_template: str, date: datetime.date, max_results: int) -> List[str]:
        events = self._get_events(calendar_id, date, max_results)
        if not events:
            self._logger.info(json.dumps({
                'event': 'calendar_summarizer:summarize:no_event',
                'calendar_id': calendar_id,
                'message': 'No event scheduled for today',
            }))
            return []
        message_template = string.Template(message_template).substitute({
            'y': str(date.year),
            'm': str(date.month),
            'd': str(date.day),
            'summarized_items': '${summarized_items}'
        })
        groups = self._grouping(events, message_template)
        summarized_items = []
        for group in groups:
            res = string.Template(message_template).substitute({
                'summarized_items': '\n'.join(group)
            })
            summarized_items.append(res)
        return summarized_items

    def _get_events(self, calendar_id: str, date: datetime.date, max_results: int):
        from_datetime = datetime.datetime(
            year=date.year,
            month=date.month,
            day=date.day,
            hour=0,
            minute=0,
            second=0,
            tzinfo=self._timezone
        )
        to_datetime = from_datetime + datetime.timedelta(days=1)
        res = self._calendar_service.events().list(
            calendarId=calendar_id,
            timeMin=from_datetime.isoformat(),
            timeMax=to_datetime.isoformat(),
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return res.get('items', [])

    def _grouping(self, events, message_template: str) -> list:
        max_length = 140
        template = string.Template(message_template).substitute({
            'summarized_items': ''
        })
        reserved_len = len(template)
        max_title_len = abs(max_length - reserved_len)
        items = []
        print(events)
        for event in events:
            start = datetime.datetime.strptime(
                event['start'].get(
                    'dateTime', event['start'].get('date')),
                    '%Y-%m-%dT%H:%M:%S%z'
            ).astimezone(self._timezone)
            items.append('{0} {1}'.format(start.strftime('%H:%M'), event['summary'][:max_title_len]))
        group: List[str] = []
        groups = [group]
        for item in items:
            group_len = reduce(lambda x, y: x + y, [len(i) for i in group], 0) + len(group) - 1
            item_len = len(item)
            if max_length - reserved_len - group_len - item_len > 0:
                group.append(item)
                continue
            else:
                group = [item]
                groups.append(group)
        return groups
