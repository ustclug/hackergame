from django.conf import settings
from django.shortcuts import redirect

from .models import Terms


class TermsRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not Terms.agreed_all_terms(request.user):
            return self.handle_terms_not_agreed()
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def handle_terms_not_agreed():
        return redirect(settings.TERMS_URL)
