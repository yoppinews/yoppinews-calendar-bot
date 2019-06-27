# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import List, Optional

import json
import yaml
import boto3
import datetime
import logging


class CalendarBotConfig:
    def __init__(self, dic: dict):
        self._dic = dic
        self._logger = CalendarBotConfig._get_logger(self.log_level)

    @staticmethod
    def initialize(stage: str, config_bucket: str, config_key_name: str) -> CalendarBotConfig:
        bucket = boto3.resource('s3').Bucket(config_bucket) if stage != 'local' \
            else boto3.resource('s3', endpoint_url='http://localstack:4572').Bucket(config_bucket)
        timestamp = datetime.datetime.utcnow().timestamp()
        config_path = '/tmp/config.' + str(timestamp)
        bucket.download_file(config_key_name, config_path)
        f = open(config_path, "r")
        dic = yaml.load(f, Loader=yaml.SafeLoader)
        f.close()
        return CalendarBotConfig(dic)

    @property
    def log_level(self) -> str:
        return self._dic.get('global_config', {}).get('log_level', 'INFO')

    @staticmethod
    def _get_logger(log_level):
        logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        numeric_level = getattr(logging, log_level.upper(), None)
        handler.setLevel(numeric_level)
        logger.setLevel(numeric_level)
        logger.handlers = [handler]
        logger.propagate = False
        return logger

    @property
    def logger(self):
        return self._logger

    @property
    def timezone(self) -> datetime.timezone:
        delta = self._dic.get('global_config', {}).get('time_delta', 0)
        return datetime.timezone(datetime.timedelta(hours=delta))

    @property
    def calendars(self) -> List[GoogleCalendar]:
        cs = self._dic.get('calendars', [])
        res = []
        for c in cs:
            res.append(GoogleCalendar.of(c))
        return res


class GoogleCalendar:
    def __init__(
        self,
        calendar_id: str,
        max_summarized_items: int,
        summarize_message_template: Optional[str],
        notify_before_event_starts: int,
        notification_message_template: Optional[str],
    ):
        self._calendar_id = calendar_id
        self._max_summarized_items = max_summarized_items
        self._summarize_message_template = summarize_message_template
        self._notify_before_event_starts = notify_before_event_starts
        self._notification_message_template = notification_message_template

    def __repr__(self):
        return json.dumps({
            'calendar_id': self._calendar_id,
            'max_summarized_items': self._max_summarized_items,
            'summarize_message_template': self._summarize_message_template,
            'notify_before_event_starts': self._notify_before_event_starts,
            'notification_message_template': self._notification_message_template
        })

    def __eq__(self, other) -> bool:
        if not isinstance(other, GoogleCalendar):
            return False
        return \
            self._calendar_id == other._calendar_id and \
            self._max_summarized_items == other._max_summarized_items and \
            self._summarize_message_template == other._summarize_message_template and \
            self._notify_before_event_starts == other._notify_before_event_starts and \
            self.notification_message_template == other._notification_message_template

    @staticmethod
    def of(dic: dict) -> GoogleCalendar:
        calendar_id = dic['calendar_id']
        max_summarized_items = dic.get('max_summarized_items', 10)
        summarize_message_template = dic.get('summarized_message_template', None)
        notify_before_event_starts = dic.get('notify_before_event_starts', 30)
        notification_message_template = dic.get('notification_message_template', None)
        return GoogleCalendar(
            calendar_id,
            max_summarized_items,
            summarize_message_template,
            notify_before_event_starts,
            notification_message_template,
        )

    @property
    def calendar_id(self) -> str:
        return self._calendar_id

    @property
    def max_summarized_items(self) -> int:
        return self._max_summarized_items

    @property
    def summarize_message_template(self) -> Optional[str]:
        return self._summarize_message_template

    @property
    def notify_before_event_starts(self) -> int:
        return self._notify_before_event_starts

    @property
    def notification_message_template(self) -> Optional[str]:
        return self._notification_message_template
