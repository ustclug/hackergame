import os.path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.views import generic


class Upload(UserPassesTestMixin, generic.TemplateView):
    template_name = settings.UPLOAD_TEMPLATE_UPLOAD

    def test_func(self):
        return self.request.user.is_staff

    def post(self, request):
        file = request.FILES['file']
        if len(file.name) < 16:
            messages.error(request, '上传失败，文件名太简单')
            return redirect('upload')
        if os.path.exists(os.path.join(settings.UPLOAD_DIR, file.name)):
            messages.error(request, '上传失败，有同名文件存在')
            return redirect('upload')
        self.save_file(file)
        messages.success(request, '上传成功')
        return redirect('upload')

    @staticmethod
    def save_file(file):
        with open(os.path.join(settings.UPLOAD_DIR, file.name), 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)
