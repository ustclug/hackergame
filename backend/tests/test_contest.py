from datetime import timedelta

import pytest
import pytz
from django.conf import settings
from django.core.exceptions import ValidationError

from contest.models import Stage, Pause
from contest.models import StageManager
from tests.conftest import stage


@pytest.fixture
def pause(stage):
    start_time = stage.start_time + timedelta(hours=1)
    end_time = stage.start_time + timedelta(hours=2)
    return Pause.objects.create(start_time=start_time, end_time=end_time)


def test_multiple_stage_line():
    stage()
    with pytest.raises(ValidationError):
        stage()


def test_pause_validation(stage):
    start_time = stage.start_time - timedelta(seconds=1)
    end_time = stage.start_time + timedelta(hours=1)
    with pytest.raises(ValidationError):
        Pause.objects.create(start_time=start_time, end_time=end_time)


def test_current_status(stage, pause):
    cur_time = None

    # monkey patch now()
    origin_now = StageManager.now
    StageManager.now = lambda cls: cur_time

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

    StageManager.now = origin_now


def test_stage(stage, pause, client):
    r = client.get('/api/stage/')
    tz = pytz.timezone(settings.TIME_ZONE)
    assert r.data['start_time'] == stage.start_time.astimezone(tz).isoformat()
    assert r.data['pause'][0]['start_time'] == pause.start_time.astimezone(tz).isoformat()


def test_get_current_stage(stage, client):
    cur_time = None

    # monkey patch now()
    origin_now = StageManager.now
    StageManager.now = lambda cls: cur_time

    cur_time = stage.start_time - timedelta(seconds=100)
    r = client.get('/api/stage/current/')
    assert r.data['status'] == 'not start'

    StageManager.now = origin_now
