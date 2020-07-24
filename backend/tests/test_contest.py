from datetime import datetime, timedelta

import pytest
import pytz
from django.conf import settings

from contest.models import Stage, Pause
from contest.models import StageManager

cur_time = None


def now(cls):
    return cur_time


# monkey patch now()
StageManager.now = now


@pytest.fixture
def stage():
    start_time = datetime(2020, 7, 24, 22, 47, 00, tzinfo=pytz.utc)
    end_time = datetime(2020, 7, 25, 12, 00, 00, tzinfo=pytz.utc)
    practice_start_time = datetime(2020, 7, 26, 8, 00, 00, tzinfo=pytz.utc)
    return Stage.objects.create(start_time=start_time, end_time=end_time,
                                practice_start_time=practice_start_time)


@pytest.fixture
def pause(stage):
    start_time = datetime(2020, 7, 25, 8, 47, 00, tzinfo=pytz.utc)
    end_time = datetime(2020, 7, 25, 9, 30, 00, tzinfo=pytz.utc)
    return Pause.objects.create(start_time=start_time, end_time=end_time)


def test_current_status(stage, pause):
    global cur_time
    cur_time = stage.start_time - timedelta(seconds=100)
    assert Stage.objects.current_status == "not start"
    cur_time = stage.start_time + timedelta(seconds=100)
    assert Stage.objects.current_status == "underway"
    cur_time = pause.start_time + timedelta(seconds=100)
    assert Stage.objects.current_status == "paused"
    cur_time = stage.end_time + timedelta(seconds=100)
    assert Stage.objects.current_status == "ended"
    cur_time = stage.practice_start_time + timedelta(seconds=100)
    assert Stage.objects.current_status == "practice"


def test_stage(stage, pause, client):
    r = client.get('/api/stage/')
    tz = pytz.timezone(settings.TIME_ZONE)
    assert r.data['start_time'] == stage.start_time.astimezone(tz).isoformat()
    assert r.data['pause'][0]['start_time'] == pause.start_time.astimezone(tz).isoformat()


def test_get_current_stage(stage, client):
    global cur_time
    cur_time = stage.start_time - timedelta(seconds=100)
    r = client.get('/api/stage/current/')
    assert r.data['status'] == 'not start'
