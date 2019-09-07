from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.views import generic

from .models import Terms


class TermsList(generic.ListView):
    template_name = 'terms/terms_list.html'

    def get_queryset(self):
        return Terms.current_terms()

    @staticmethod
    def post(request):
        if not request.user.is_authenticated:
            raise PermissionDenied
        for term in request.POST.getlist('terms'):
            term_obj = Terms.objects.get(pk=term)
            if request.user in term_obj.banned.all():
                return redirect(settings.TERMS_REDIRECT_URL)
        request.user.terms_set.set(request.POST.getlist('terms'))
        return redirect(settings.TERMS_REDIRECT_URL)
