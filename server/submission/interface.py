from datetime import timedelta

from server.challenge.interface import Challenge
from server.user.interface import User
from server.context import Context
from server.exceptions import Error, NotFound, WrongArguments, WrongFormat
from . import models


class SlowDown(Error):
    code = 'slow_down'
    message = '提交过于频繁'


class Submission:
    @classmethod
    def submit(cls, context, user, challenge, text):
        if context.user.pk != user:
            User.test_permission(context)
        if len(text) > 200:
            raise WrongFormat('Flag 不应超过 200 个字符')
        user = User.get(context, user)
        challenge = Challenge.get(context, challenge)
        try:
            latest = (
                models.Submission.objects
                .filter(user=user.pk, challenge=challenge.pk)
                .latest('time')
            )
        except models.Submission.DoesNotExist:
            pass
        else:
            if latest.time + timedelta(seconds=10) > context.time:
                raise SlowDown('提交过于频繁，请 10 秒后再试')
        obj = models.Submission.objects.create(
            user=user.pk,
            group=user.group,
            challenge=challenge.pk,
            text=text,
            time=context.time,
        )
        matches, violations = challenge.check_flag_with_violations(text)
        queryset = models.FlagClear.objects.filter(user=user.pk,
                                                   challenge=challenge.pk)
        flags = {i.flag for i in queryset}
        match_flags = {i['index'] for i in matches}
        for flag in match_flags - flags:
            models.FlagClear.objects.create(
                submission=obj,
                user=user.pk,
                group=user.group,
                challenge=challenge.pk,
                flag=flag,
                time=context.time,
            )
            if user.group != 'staff':
                models.FlagFirst.objects.get_or_create(
                    challenge=challenge.pk,
                    flag=flag,
                    group=None,
                    defaults={'user': user.pk, 'time': context.time},
                )
            models.FlagFirst.objects.get_or_create(
                challenge=challenge.pk,
                flag=flag,
                group=user.group,
                defaults={'user': user.pk, 'time': context.time},
            )
        for f, u in violations:
            models.FlagViolation.objects.create(
                submission=obj,
                violation_flag=f['index'],
                violation_user=u,
            )
        if match_flags - flags:
            if (flags | match_flags).issuperset(range(len(challenge.flags))):
                models.ChallengeClear.objects.create(
                    user=user.pk,
                    group=user.group,
                    challenge=challenge.pk,
                    time=context.time,
                )
                if user.group != 'staff':
                    models.ChallengeFirst.objects.get_or_create(
                        challenge=challenge.pk,
                        group=None,
                        defaults={'user': user.pk, 'time': context.time},
                    )
                models.ChallengeFirst.objects.get_or_create(
                    challenge=challenge.pk,
                    group=user.group,
                    defaults={'user': user.pk, 'time': context.time},
                )
            score = sum(i['score'] for i in matches if i['index'] not in flags)
            cls._add_score(user.pk, user.group, context.time, score,
                           challenge.category)
        return matches

    @classmethod
    def _add_score(cls, user, group, time, score, category=None):
        if category is not None:
            cls._add_score(user, group, time, score)
        try:
            o = models.Score.objects.get(user=user, category=category)
            o.score += score
            o.time = time
            o.save()
        except models.Score.DoesNotExist:
            models.Score.objects.create(
                user=user,
                group=group,
                category=category,
                score=score,
                time=time,
            )

    @classmethod
    def get_log(cls, context, *, after=None, before=None, limit=None,
                challenge=None, group=None, match=None):
        if after is not None and before is not None:
            raise WrongArguments()
        User.test_permission(context, 'submission.full', 'submission.view')
        queryset = models.Submission.objects.order_by('-pk')
        if after is not None:
            queryset = queryset.filter(pk__lt=after)
        if before is not None:
            queryset = queryset.filter(pk__gt=before).reverse()
        if challenge is not None:
            queryset = queryset.filter(challenge=challenge)
        if group is not None:
            queryset = queryset.filter(group=group)
        if match is not None:
            queryset = queryset.filter(flagclear__isnull=not match)
        queryset = list(queryset.values(
            'pk', 'user', 'challenge', 'text', 'time',
            flag=models.models.F('flagclear__flag'),
        )[slice(limit)])
        if before is not None:
            queryset.reverse()
        return queryset

    @classmethod
    def get_violations(cls, context, *, challenge=None, group=None):
        User.test_permission(context, 'submission.full', 'submission.view')
        queryset = models.FlagViolation.objects
        if challenge is not None:
            queryset = queryset.filter(submission__challenge=challenge)
        if group is not None:
            queryset = queryset.filter(submission__group=group)
        return list(queryset.values(
            'violation_flag', 'violation_user',
            user=models.models.F('submission__user'),
            challenge=models.models.F('submission__challenge'),
            time=models.models.F('submission__time'),
        ))

    # noinspection PyUnusedLocal
    @classmethod
    def get_user_progress(cls, context, user):
        return {
            'challenges': list(
                models.ChallengeClear.objects
                .filter(user=user)
                .values('challenge', 'time')
            ),
            'flags': list(
                models.FlagClear.objects
                .filter(user=user)
                .values('challenge', 'flag', 'time')
            ),
            'scores': list(
                models.Score.objects
                .filter(user=user)
                .values('category', 'score', 'time')
            ),
        }

    @classmethod
    def get_user_ranking(cls, context, user, *, category=None, group=None):
        try:
            obj = models.Score.objects.get(user=user, category=category)
            score, time = obj.score, obj.time
        except models.Score.DoesNotExist:
            score, time = 0, context.time
        return {
            'ranking': (
                cls._filter_group(models.Score.objects, group)
                .filter(category=category)
                .filter(models.models.Q(score__gt=score)
                        | models.models.Q(score=score, time__lt=time))
                .count() + 1
            ),
            'total': (
                cls._filter_group(models.Score.objects, group)
                .filter(category=category)
                .count()
            ),
        }

    @classmethod
    def get_user_history(cls, context, user):
        challenges = Challenge.get_all(context.copy(elevated=True))
        flags = {i.pk: i.flags for i in challenges}
        score = 0
        history = []
        for i in models.FlagClear.objects.filter(user=user).order_by('time'):
            score += flags[i.challenge][i.flag]['score']
            history.append({'time': i.time, 'score': score})
        return history

    @classmethod
    def _filter_group(cls, queryset, group):
        if group is None:
            return queryset.exclude(group='staff')
        else:
            return queryset.filter(group=group)

    # noinspection PyUnusedLocal
    @classmethod
    def get_clear_count(cls, context, *, group=None):
        return {
            'challenges': list(
                cls._filter_group(models.ChallengeClear.objects, group)
                .values('challenge')
                .annotate(count=models.models.Count('user'))
            ),
            'flags': list(
                cls._filter_group(models.FlagClear.objects, group)
                .values('challenge', 'flag')
                .annotate(count=models.models.Count('user'))
            ),
        }

    # noinspection PyUnusedLocal
    @classmethod
    def get_first(cls, context, *, group=None):
        if group in {'staff', 'other'}:
            User.test_permission(context, 'submission.full', 'submission.view')
        return {
            'challenges': list(
                models.ChallengeFirst.objects
                .filter(group=group)
                .values('challenge', 'user', 'time')
            ),
            'flags': list(
                models.FlagFirst.objects
                .filter(group=group)
                .values('challenge', 'flag', 'user', 'time')
            ),
        }

    # noinspection PyUnusedLocal
    @classmethod
    def get_board(cls, context, *, limit=None,
                  category=None, group=None):
        if group in {'staff', 'other'}:
            User.test_permission(context, 'submission.full', 'submission.view')
        return list(
            cls._filter_group(models.Score.objects, group)
            .filter(category=category)
            .order_by('-score', 'time')
            .values('user', 'score', 'time')
            [slice(limit)]
        )

    @classmethod
    def regen_all(cls, context):
        """重算所有缓存，只有通过命令行提权后才能调用"""
        User.test_permission(context)
        for obj in models.Submission.objects.all():
            try:
                obj.group = User.get(context, obj.user).group
                obj.save()
            except NotFound:
                pass
        for obj in models.FlagClear.objects.all():
            try:
                user = User.get(context, obj.user)
                obj.group = user.group
                challenge = Challenge.get(context, obj.challenge)
                if obj.flag not in range(len(challenge.flags)):
                    raise NotFound
                obj.save()
            except NotFound:
                obj.delete()
        for challenge in Challenge.get_all(context):
            cls._regen_challenge_clear(challenge)
        models.ChallengeFirst.objects.all().delete()
        models.FlagFirst.objects.all().delete()
        cls._refill_first()
        cls._regen_score()

    @classmethod
    def _refill_first(cls):
        """尝试把 ChallengeFirst 和 FlagFirst 中的空位都填上"""
        for challenge in Challenge.get_all(Context(elevated=True)):
            for group in {None, *User.groups}.difference(
                models.ChallengeFirst.objects
                .filter(challenge=challenge.pk)
                .values_list('group', flat=True)
            ):
                try:
                    first = (
                        cls._filter_group(models.ChallengeClear.objects, group)
                        .filter(challenge=challenge.pk)
                        .earliest('time')
                    )
                    models.ChallengeFirst.objects.create(
                        challenge=challenge.pk,
                        group=group,
                        user=first.user,
                        time=first.time,
                    )
                except models.ChallengeClear.DoesNotExist:
                    pass
            for flag in range(len(challenge.flags)):
                for group in {None, *User.groups}.difference(
                    models.FlagFirst.objects
                    .filter(challenge=challenge.pk, flag=flag)
                    .values_list('group', flat=True)
                ):
                    try:
                        first = (
                            cls._filter_group(models.FlagClear.objects, group)
                            .filter(challenge=challenge.pk, flag=flag)
                            .earliest('time')
                        )
                        models.FlagFirst.objects.create(
                            challenge=challenge.pk,
                            flag=flag,
                            group=group,
                            user=first.user,
                            time=first.time,
                        )
                    except models.FlagClear.DoesNotExist:
                        pass

    @classmethod
    def _regen_score(cls):
        models.Score.objects.all().delete()
        cs = {i.pk: i.json for i in Challenge.get_all(Context(elevated=True))}
        for i in models.FlagClear.objects.order_by('time').iterator():
            if cs[i.challenge]['enabled']:
                cls._add_score(i.user, i.group, i.time,
                               cs[i.challenge]['flags'][i.flag]['score'],
                               cs[i.challenge]['category'])

    @classmethod
    def _regen_challenge_clear(cls, challenge: Challenge):
        models.ChallengeClear.objects.filter(challenge=challenge.pk).delete()
        for i in (
            models.FlagClear.objects
            .filter(challenge=challenge.pk)
            .values('user', 'group')
            .annotate(count=models.models.Count('flag'),
                      time=models.models.Max('time'))
        ):
            if i.pop('count') == len(challenge.flags):
                models.ChallengeClear.objects.create(challenge=challenge.pk,
                                                     **i)

    @classmethod
    def _challenge_event(cls, old, new):
        context = Context(elevated=True)
        if old is None:
            return
        if new is None:
            models.ChallengeClear.objects.filter(challenge=old['pk']).delete()
            models.FlagClear.objects.filter(challenge=old['pk']).delete()
            models.ChallengeFirst.objects.filter(challenge=old['pk']).delete()
            models.FlagFirst.objects.filter(challenge=old['pk']).delete()
            if old['enabled']:
                cls._regen_score()
            return
        if len(new['flags']) != len(old['flags']):
            models.FlagClear.objects.filter(
                challenge=old['pk'], flag__gte=len(new['flags'])).delete()
            cls._regen_challenge_clear(Challenge.get(context, old['pk']))
            models.ChallengeFirst.objects.filter(challenge=old['pk']).delete()
            models.FlagFirst.objects.filter(challenge=old['pk']).delete()
            cls._refill_first()
        if not old['enabled'] and not new['enabled']:
            return
        if new['enabled'] != old['enabled']:
            cls._regen_score()
            return
        if new['category'] != old['category']:
            cls._regen_score()
            return
        old_flag_scores = [i['score'] for i in old['flags']]
        new_flag_scores = [i['score'] for i in new['flags']]
        if new_flag_scores != old_flag_scores:
            cls._regen_score()
            return

    @classmethod
    def _user_event(cls, old, new):
        if old is None:
            return
        if new is None:
            models.ChallengeClear.objects.filter(user=old['pk']).delete()
            models.FlagClear.objects.filter(user=old['pk']).delete()
            models.ChallengeFirst.objects.filter(user=old['pk']).delete()
            models.FlagFirst.objects.filter(user=old['pk']).delete()
            cls._refill_first()
            models.Score.objects.filter(user=old['pk']).delete()
            return
        if new['group'] != old['group']:
            models.Submission.objects.filter(user=old['pk']) \
                .update(group=new['group'])
            models.ChallengeClear.objects.filter(user=old['pk']) \
                .update(group=new['group'])
            models.FlagClear.objects.filter(user=old['pk']) \
                .update(group=new['group'])
            models.ChallengeFirst.objects.filter(user=old['pk']).delete()
            models.ChallengeFirst.objects.filter(group=new['group']).delete()
            models.FlagFirst.objects.filter(user=old['pk']).delete()
            models.FlagFirst.objects.filter(group=new['group']).delete()
            cls._refill_first()
            models.Score.objects.filter(user=old['pk']) \
                .update(group=new['group'])

    @classmethod
    def app_ready(cls):
        Challenge.subscribers.append(cls._challenge_event)
        User.subscribers.append(cls._user_event)
