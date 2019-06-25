import logging
import datetime

from src.summarize_schedules.calendar_summarizer import GoogleCalendarSummarizer


def test_grouping():
    s = GoogleCalendarSummarizer({}, datetime.timezone(datetime.timedelta(hours=0)), logging.Logger(name='hoge'))
    events = [
        {
            'kind': 'calendar#event',
            'etag': '"012345"',
            'id': '012345',
            'status': 'confirmed',
            'htmlLink': 'https://www.google.com/calendar/event?eid=',
            'created': '2019-06-17T08:29:15.000Z',
            'updated': '2019-06-24T14:51:11.964Z',
            'summary': 'summary00:123456789:123456789:123456789:123456789:123456789:123456789:123456789:123456789:',
            'description': 'description',
            'start': {
                'dateTime': '2019-06-25T12:30:00+09:00'
            },
            'end': {
                'dateTime': '2019-06-25T13:30:00+09:00'
            },
        },
        {
            'kind': 'calendar#event',
            'etag': '"012345"',
            'id': '012345',
            'status': 'confirmed',
            'htmlLink': 'https://www.google.com/calendar/event?eid=',
            'created': '2019-06-17T08:29:15.000Z',
            'updated': '2019-06-24T14:51:11.964Z',
            'summary': 'summary00:123456789:123456789:123456789:123456789:123456789:123456789:123456789:123456789:',
            'description': 'description',
            'start': {
                'dateTime': '2019-06-25T12:30:00+09:00'
            },
            'end': {
                'dateTime': '2019-06-25T13:30:00+09:00'
            },
        },
    ]
    res = s._grouping(events, '${summarized_items}')
    assert len(res) == 2
    for i in res:
        assert len(i) == 1
        assert i[0] == '03:30 summary00:123456789:123456789:123456789:' \
                       '123456789:123456789:123456789:123456789:123456789:'


