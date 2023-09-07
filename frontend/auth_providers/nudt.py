from datetime import timedelta

from django.urls import path

from .base import AllowlistEmailValidator
from .external import ExternalLoginView, ExternalGetCodeView


class LoginView(ExternalLoginView):
    template_context = {'provider_name': '国防科技大学'}
    provider = 'nudt'
    group = 'nudt'


class GetCodeView(ExternalGetCodeView):
    provider = 'nudt'
    duration = timedelta(hours=1)
    # validate_identity = AllowlistEmailValidator([])


urlpatterns = [
    path('nudt/login/', LoginView.as_view()),
    path('nudt/get_code/', GetCodeView.as_view()),
]
