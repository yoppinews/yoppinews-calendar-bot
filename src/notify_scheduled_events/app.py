# -*- coding: utf-8 -*-

import os
import json
import boto3
import string
import datetime

from typing import List
from logging import Logger

from message import TweetMessage
from scheduled_event import GoogleCalendarAPI, ScheduledEventsRepository
from calendar_config import CalendarBotConfig, GoogleCalendar

# env_vars
stage = os.environ['Stage']
config_bucket = os.environ['ConfigBucket']
config_key_name = os.environ['ConfigKeyName']
cache_bucket = os.environ['CacheBucket']
tweet_topic = os.environ['TweetTopic']
google_api_key = os.environ['GoogleAPIKey']

s3 = boto3.client('s3') if stage != 'local' \
    else boto3.client('s3',  endpoint_url='http://localstack:4572')
sns = boto3.client('sns') if stage != 'local' \
    else boto3.client('sns', endpoint_url='http://localstack:4575')


def lambda_handler(_, __):
    config = CalendarBotConfig.initialize(stage, config_bucket, config_key_name)
    api = GoogleCalendarAPI(google_api_key, config.timezone)
    handle(api, config.calendars, config.timezone, config.logger)
    return {}


def handle(
    api: GoogleCalendarAPI,
    calendars: List[GoogleCalendar],
    timezone: datetime.timezone,
    logger: Logger
):
    for c in calendars:
        if c.notification_message_template is None:
            continue
        end = datetime.datetime.now(timezone) + datetime.timedelta(minutes=c.notify_before_event_starts)
        start = end - datetime.timedelta(minutes=3)
        repo = ScheduledEventsRepository(s3, cache_bucket, api, c.calendar_id)
        events = repo.get_events(start, end)
        for e in events:
            if e.notify_needed:
                text = string.Template(c.notification_message_template).substitute(e.dictionary)
                tweet(TweetMessage(text), logger)
                repo.mark_as_notified(e.item_id)


def tweet(m: TweetMessage, logger: Logger):
    j = json.dumps(m.dictionary, ensure_ascii=False)
    logger.debug(json.dumps({
        'event': 'summarize_schedules:tweet:item',
        'details': m.dictionary
    }, ensure_ascii=False))
    res = sns.publish(
        TopicArn=tweet_topic,
        Message=j,
    )
    logger.info(json.dumps({
        'event': 'summarize_schedules:tweet:message_id',
        'details': {'text': m.status, 'return': res}
    }, ensure_ascii=False))
