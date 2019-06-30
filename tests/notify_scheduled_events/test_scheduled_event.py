import datetime

from src.notify_scheduled_events.scheduled_event import ScheduledEvent


def test_scheduled_event():
    now = datetime.datetime.now()
    e = ScheduledEvent(
        item_id='id',
        title='title',
        description='description',
        start=now,
        notify_needed=False
    )
    assert e.description == 'description'


def test_scheduled_event_with_html_tags():
    now = datetime.datetime.now()
    e = ScheduledEvent(
        item_id='id',
        title='title',
        description='<a href="page1">description</a>',
        start=now,
        notify_needed=False
    )
    assert e.description == 'description'


def test_scheduled_event_with_nbsp():
    now = datetime.datetime.now()
    e = ScheduledEvent(
        item_id='id',
        title='title',
        description='<a href="page1">description&nbsp;description</a>',
        start=now,
        notify_needed=False
    )
    assert e.description == 'description' + chr(0x00a0) + 'description'
