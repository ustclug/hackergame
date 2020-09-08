from datetime import timedelta
from contextlib import contextmanager

import pytest
import pytz
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import status

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


@contextmanager
def monkey_patch_now(cur_time):
    origin_now = StageManager._now
    StageManager._now = lambda cls: cur_time
    yield cur_time
    StageManager._now = origin_now


@pytest.fixture
def contest_status(stage, pause):
    return (
        (stage.start_time - timedelta(seconds=100), 'not start'),
        (stage.start_time + timedelta(seconds=100), 'underway'),
        (pause.start_time + timedelta(seconds=100), 'paused'),
        (stage.end_time + timedelta(seconds=100), 'ended'),
        (stage.practice_start_time + timedelta(seconds=100), 'practice')
    )


def test_current_status(contest_status):
    for cur in contest_status:
        with monkey_patch_now(cur[0]):
            assert Stage.objects.current_status == cur[1]


def test_stage(stage, pause, client):
    r = client.get('/api/stage/')
    tz = pytz.timezone(settings.TIME_ZONE)
    assert r.data['start_time'] == stage.start_time.astimezone(tz).isoformat()
    assert r.data['pause'][0]['start_time'] == pause.start_time.astimezone(tz).isoformat()


def test_get_current_stage(stage, client):
    cur_time = stage.start_time - timedelta(seconds=100)
    with monkey_patch_now(cur_time):
        r = client.get('/api/stage/current/')
        assert r.data['status'] == 'not start'


def test_submission(contest_status, challenge, client):
    data = {
        'challenge': challenge.id,
        'flag': "any"
    }
    for cur in contest_status:
        with monkey_patch_now(cur[0]):
            r = client.post('/api/submission/', data)
            if cur[1] in ('not start', 'paused', 'ended'):
                assert r.status_code == status.HTTP_403_FORBIDDEN
                assert '比赛当前阶段无法提交' in r.data['detail']
            else:
                assert r.status_code == status.HTTP_200_OK


def test_view_challenge(contest_status, challenge, client):
    for cur in contest_status:
        with monkey_patch_now(cur[0]):
            r = client.get('/api/challenge/')
            if cur[1] in ('not start', 'paused'):
                assert r.status_code == status.HTTP_403_FORBIDDEN
                assert '比赛当前阶段无法查看题目' in r.data['detail']
            else:
                assert r.status_code == status.HTTP_200_OK
