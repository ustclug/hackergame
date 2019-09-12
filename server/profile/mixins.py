from django.shortcuts import redirect


class ProfileRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.profile.ok:
            return self.handle_profile_not_updated()
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def handle_profile_not_updated():
        return redirect('profile')
