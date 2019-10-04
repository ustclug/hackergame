from server.challenge.interface import Challenge
from server.user.interface import User
from server.context import Context
from server.exceptions import WrongFormat
from . import models


class Submission:
    @classmethod
    def submit(cls, context, user, challenge, text):
        if context.user.pk != user:
            User.test_permission(context)
        if len(text) > 100:
            raise WrongFormat('Flag 不应超过 100 个字符')
        user = User.get(context, user)
        challenge = Challenge.get(context, challenge)
        obj = models.Submission.objects.create(
            user=user.pk,
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
                flag=f['index'],
                user=u,
            )
        if match_flags - flags:
            if (flags | match_flags).issuperset(range(len(challenge.flags))):
                models.ChallengeClear.objects.create(
                    user=user.pk,
                    group=user.group,
                    challenge=challenge.pk,
                    time=context.time,
                )
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
    def get_log(cls, context, start=None, limit=None):
        User.test_permission(context, 'submission.full')
        return list(
            models.Submission.objects
            .order_by('-pk')
            .filter(**({} if start is None else {'pk__lte': start}))
            .values(
                'pk', 'user', 'challenge', 'text', 'time',
                flag=models.models.F('flagclear__flag'),
            )
            [slice(limit)]
        )

    @classmethod
    def get_violations(cls, context):
        User.test_permission(context, 'submission.full')
        return list(models.FlagViolation.objects.values(
            user=models.models.F('submission__user'),
            challenge=models.models.F('submission__challenge'),
            time=models.models.F('submission__time'),
            violation_flag=models.models.F('flag'),
            violation_user=models.models.F('user'),
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
        }

    # noinspection PyUnusedLocal
    @classmethod
    def get_clear_count(cls, context, *, group=None):
        return {
            'challenges': list(
                models.ChallengeClear.objects
                .filter(**({} if group is None else {'group': group}))
                .values('challenge')
                .annotate(count=models.models.Count('user'))
            ),
            'flags': list(
                models.FlagClear.objects
                .filter(**({} if group is None else {'group': group}))
                .values('challenge', 'flag')
                .annotate(count=models.models.Count('user'))
            ),
        }

    # noinspection PyUnusedLocal
    @classmethod
    def get_first(cls, context, *, group=None):
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
        return list(
            models.Score.objects
            .filter(category=category)
            .filter(**({} if group is None else {'group': group}))
            .order_by('-score', 'time')
            .values('user', 'score', 'time')
            [slice(limit)]
        )

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
                    first = models.ChallengeClear.objects.filter(
                        challenge=challenge.pk,
                        **({} if group is None else {'group': group}),
                    ).earlist('time')
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
                        first = models.FlagClear.objects.filter(
                            challenge=challenge.pk,
                            flag=flag,
                            **({} if group is None else {'group': group}),
                        ).earlist('time')
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
    def _challenge_event(cls, old, new):
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
            models.ChallengeClear.objects.filter(challenge=old['pk']).delete()
            models.FlagClear.objects.filter(
                challenge=old['pk'], flag__gte=len(new['flags'])).delete()
            for i in (
                models.FlagClear.objects
                .filter(challenge=old['pk'])
                .values('user', 'group')
                .annotate(count=models.models.Count('flag'),
                          time=models.models.Max('time'))
            ):
                if i.pop('count') == len(new['flags']):
                    models.ChallengeClear.objects.create(challenge=old['pk'],
                                                         **i)
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
            models.ChallengeClear.objects.filter(user=old['pk']) \
                .update(group=new['group'])
            models.FlagClear.objects.filter(user=old['pk']) \
                .update(group=new['group'])
            models.ChallengeFirst.objects.filter(user=old['pk'],
                                                 group=old['group']).delete()
            models.ChallengeFirst.objects.filter(group=new['group']).delete()
            models.FlagFirst.objects.filter(user=old['pk'],
                                            group=old['group']).delete()
            models.FlagFirst.objects.filter(group=new['group']).delete()
            cls._refill_first()
            models.Score.objects.filter(user=old['pk']) \
                .update(group=new['group'])


# noinspection PyProtectedMember
Challenge.subscribers.append(Submission._challenge_event)
# noinspection PyProtectedMember
User.subscribers.append(Submission._user_event)
