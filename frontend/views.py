import json

from django.contrib import messages
from django.contrib.admin import site
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views import View

from server.announcement.interface import Announcement
from server.challenge.interface import Challenge
from server.submission.interface import Submission
from server.terms.interface import Terms, TermsRequired
from server.trigger.interface import Trigger
from server.user.interface import User, LoginRequired, ProfileRequired
from server.context import Context
from server.exceptions import Error, NotFound, WrongFormat


# noinspection PyMethodMayBeStatic
class HubView(View):
    def get(self, request):
        context = Context.from_request(request)
        try:
            challenges = Challenge.get_enabled(context)
            challenges = {'value': [obj.json for obj in challenges]}
        except ProfileRequired as e:
            messages.info(request, e.message)
            return redirect('profile')
        except TermsRequired as e:
            messages.info(request, e.message)
            return redirect('terms')
        except Error as e:
            challenges = {'error': e.json}
        try:
            announcement = Announcement.get_latest(context).json
        except NotFound:
            announcement = None
        user = User.get(context, request.user.pk)
        return TemplateResponse(request, 'hub.html', {
            'announcement': announcement,
            'challenges': challenges,
            'progress': Submission.get_user_progress(context, user.pk),
            'ranking': Submission.get_user_ranking(context, user.pk,
                                                   group=user.group),
            'clear_count': Submission.get_clear_count(context),
        })

    def post(self, request):
        try:
            matches = Submission.submit(Context.from_request(request),
                                        request.user.pk,
                                        request.POST['challenge'],
                                        request.POST['flag'].strip())
            if matches:
                messages.success(request, '答案正确')
            else:
                messages.error(request, '答案错误')
        except Error as e:
            messages.info(request, e.message)
        return redirect('hub')


# noinspection PyMethodMayBeStatic
class AnnouncementsView(View):
    def get(self, request):
        context = Context.from_request(request)
        return TemplateResponse(request, 'announcements.html', {
            'announcements': Announcement.get_all(context),
        })


# noinspection PyMethodMayBeStatic
class BoardView(View):
    def get(self, request):
        context = Context.from_request(request)
        return TemplateResponse(request, 'board.html', {
            'filters': {
                'category': request.GET.get('category', None),
                'group': request.GET.get('group', None),
            },
            'users': {u.pk: u.display_name for u in User.get_all(context)},
        })


# noinspection PyMethodMayBeStatic
class FirstView(View):
    def get(self, request):
        context = Context.from_request(request)
        return TemplateResponse(request, 'first.html', {
            'filters': {
                'group': request.GET.get('group', None),
            },
            'users': {u.pk: u.display_name for u in User.get_all(context)},
            'challenges': [c.json for c in Challenge.get_enabled(context)],
        })


# noinspection PyMethodMayBeStatic
class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('hub')


# noinspection PyMethodMayBeStatic
class ProfileView(View):
    def get(self, request):
        try:
            User.test_authenticated(Context.from_request(request))
        except LoginRequired:
            return redirect('hub')
        return TemplateResponse(request, 'profile.html')

    def post(self, request):
        try:
            user = User.get(Context.from_request(request), request.user.pk)
            user.update(**json.loads(request.body))
            return JsonResponse({})
        except WrongFormat as e:
            return JsonResponse({'error': e.json}, status=400)


# noinspection PyMethodMayBeStatic
class TermsView(View):
    def get(self, request):
        terms = Terms.get_enabled(Context.from_request(request))
        return TemplateResponse(request, 'terms.html', {'terms': terms})

    def post(self, request):
        context = Context.from_request(request)
        try:
            User.test_authenticated(context)
        except LoginRequired:
            return redirect('hub')
        for pk in request.POST.getlist('terms'):
            Terms.get(context, pk=pk).agree(request.user.pk)
        return redirect('hub')


# noinspection PyMethodMayBeStatic
class BaseAdminView(View):
    title = None
    template = None

    def get_extra_context(self, user):
        return {}

    def get(self, request):
        return TemplateResponse(request, self.template, {
            **site.each_context(request),
            **self.get_extra_context(Context.from_request(request)),
            'title': self.title,
        })

    def post(self, request):
        body = json.loads(request.body)
        method = body['method']
        args = body.get('args', {})
        try:
            method = getattr(self, f'do_{method}')
            value = method(Context.from_request(request), **args)
            return JsonResponse({'value': value})
        except Error as e:
            return JsonResponse({'error': e.json}, status=400)


# noinspection PyMethodMayBeStatic
class AnnouncementAdminView(BaseAdminView):
    title = 'Announcement'
    template = 'admin_announcement.html'

    def do_get_all(self, context):
        return [obj.json for obj in Announcement.get_all(context)]

    def do_save(self, context, pk, **kwargs):
        kwargs = {k: kwargs[k] for k in kwargs
                  if k in Announcement.update_fields}
        if pk is None:
            return Announcement.create(context, **kwargs).json
        else:
            return Announcement.get(context, pk).update(**kwargs)

    # noinspection PyUnusedLocal
    def do_delete(self, context, pk, **kwargs):
        return Announcement.get(context, pk).delete()


# noinspection PyMethodMayBeStatic
class ChallengeAdminView(BaseAdminView):
    title = 'Challenge'
    template = 'admin_challenge.html'

    def do_get_all(self, context):
        return [obj.json for obj in Challenge.get_all(context)]

    def do_save(self, context, pk, **kwargs):
        kwargs = {k: kwargs[k] for k in kwargs if k in Challenge.update_fields}
        if pk is None:
            return Challenge.create(context, **kwargs).json
        else:
            return Challenge.get(context, pk).update(**kwargs)

    # noinspection PyUnusedLocal
    def do_delete(self, context, pk, **kwargs):
        return Challenge.get(context, pk).delete()


# noinspection PyMethodMayBeStatic
class SubmissionAdminView(BaseAdminView):
    title = 'Submission'
    template = 'admin_submission.html'

    def get_extra_context(self, context):
        return {
            'users': {u.pk: u.display_name for u in User.get_all(context)},
            'challenges': [c.json for c in Challenge.get_all(context)],
        }

    def do_get_log(self, context, **kwargs):
        return Submission.get_log(context, **kwargs)

    def do_get_violations(self, context):
        return Submission.get_violations(context)

    def do_get_user_progress(self, context, **kwargs):
        return Submission.get_user_progress(context, **kwargs)

    def do_get_user_history(self, context, **kwargs):
        return Submission.get_user_history(context, **kwargs)

    def do_get_clear_count(self, context, **kwargs):
        return Submission.get_clear_count(context, **kwargs)

    def do_get_first(self, context, **kwargs):
        return Submission.get_first(context, **kwargs)

    def do_get_board(self, context, **kwargs):
        return Submission.get_board(context, **kwargs)


# noinspection PyMethodMayBeStatic
class TermsAdminView(BaseAdminView):
    title = 'Terms'
    template = 'admin_terms.html'

    def do_get_all(self, context):
        return [obj.json for obj in Terms.get_all(context)]

    def do_save(self, context, pk, **kwargs):
        kwargs = {k: kwargs[k] for k in kwargs if k in Terms.update_fields}
        if pk is None:
            return Terms.create(context, **kwargs).json
        else:
            return Terms.get(context, pk).update(**kwargs)

    # noinspection PyUnusedLocal
    def do_delete(self, context, pk, **kwargs):
        return Terms.get(context, pk).delete()


# noinspection PyMethodMayBeStatic
class TriggerAdminView(BaseAdminView):
    title = 'Trigger'
    template = 'admin_trigger.html'

    def do_get_all(self, context):
        return [obj.json for obj in Trigger.get_all(context)]

    def do_save(self, context, pk, **kwargs):
        kwargs = {k: kwargs[k] for k in kwargs if k in Trigger.update_fields}
        if pk is None:
            return Trigger.create(context, **kwargs).json
        else:
            return Trigger.get(context, pk).update(**kwargs)

    # noinspection PyUnusedLocal
    def do_delete(self, context, pk, **kwargs):
        return Trigger.get(context, pk).delete()


# noinspection PyMethodMayBeStatic
class UserAdminView(BaseAdminView):
    title = 'User'
    template = 'admin_user.html'

    def do_get_all(self, context):
        return [obj.json for obj in User.get_all(context)]

    def do_save(self, context, pk, **kwargs):
        kwargs = {k: kwargs[k] for k in kwargs if k in User.update_fields}
        return User.get(context, pk).update(**kwargs)
