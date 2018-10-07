from hashlib import sha3_256
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
        if len(file.name) > 20:
            messages.error(request, '上传失败，请使用简单文件名')
            return redirect('upload')
        hashobj = sha3_256()
        for chunk in file.chunks():
            hashobj.update(chunk)
        d = hashobj.hexdigest()
        try:
            os.mkdir(os.path.join(settings.UPLOAD_DIR, d))
        except FileExistsError:
            pass
        with open(os.path.join(settings.UPLOAD_DIR, d, file.name), 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)
        messages.success(request, f'上传成功，URL: /file/{d}/{file.name}')
        return redirect('upload')
