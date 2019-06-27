import datetime

from src.layers.shared_files.python.calendar_config import CalendarBotConfig, GoogleCalendar


def test_calendar_bot_config_empty():
    config = CalendarBotConfig({})
    assert config.log_level == 'INFO'
    assert config.timezone == datetime.timezone(datetime.timedelta(hours=0))
    assert config.calendars == []


def test_calendar_bot_config():
    config = CalendarBotConfig({
        'global_config': {
            'log_level': 'DEBUG',
            'time_delta': -4
        },
        'calendars': [
            {
                'calendar_id': 'id01@group.calendar.google.com',
                'max_summarized_items': 40,
                'summarized_message_template': '${y}/${m}/${d}'
                                               '${summarized_items}'
                                               '#hashtag1 example.com',
                'notify_before_event_starts': 30,
                'notification_message_template': '${title}'
            },
            {
                'calendar_id': 'id02@group.calendar.google.com',
            },
        ]
    })
    assert config.log_level == 'DEBUG'
    assert config.timezone == datetime.timezone(datetime.timedelta(hours=-4))
    calendars = config.calendars
    assert calendars[0] == GoogleCalendar(
        calendar_id='id01@group.calendar.google.com',
        max_summarized_items=40,
        summarize_message_template='${y}/${m}/${d}'
                                   '${summarized_items}'
                                   '#hashtag1 example.com',
        notify_before_event_starts=30,
        notification_message_template='${title}'
    )
    assert calendars[1] == GoogleCalendar(
        calendar_id='id02@group.calendar.google.com',
        max_summarized_items=10,
        summarize_message_template=None,
        notify_before_event_starts=30,
        notification_message_template=None
    )
