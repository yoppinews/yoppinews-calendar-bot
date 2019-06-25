# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import json
import boto3
import datetime
from typing import List
from logging import Logger
from googleapiclient.discovery import build

from message import TweetMessage
from calendar_config import CalendarBotConfig, GoogleCalendar
from calendar_summarizer import GoogleCalendarSummarizer


# env_vars
stage = os.environ['Stage']
config_bucket = os.environ['ConfigBucket']
config_key_name = os.environ['ConfigKeyName']
tweet_topic = os.environ['TweetTopic']
google_api_key = os.environ['GoogleAPIKey']

sns = boto3.client('sns')
service = build('calendar', 'v3', developerKey=google_api_key)


def lambda_handler(_, __):
    config = CalendarBotConfig.initialize(stage, config_bucket, config_key_name)
    summarizer = GoogleCalendarSummarizer(service, config.timezone, config.logger)
    handle(summarizer, config.calendars, config.timezone, config.logger)
    return {}


def handle(
    summarizer: GoogleCalendarSummarizer,
    calendars: List[GoogleCalendar],
    timezone: datetime.timezone,
    logger: Logger
):
    date = datetime.datetime.now(timezone).date()
    for c in calendars:
        if c.summarize_message_template is None:
            continue
        summaries = summarizer.summarize(c.calendar_id, c.summarize_message_template, date, c.max_summarized_items)
        for s in summaries:
            message = TweetMessage(s)
            tweet(message, logger)


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
