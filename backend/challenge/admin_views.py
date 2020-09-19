import pathlib
import uuid

from django import forms
from django.views.generic.edit import View
from django.shortcuts import render
from django.conf import settings


class ImageUploadForm(forms.Form):
    file_field = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        label='待上传的图片'
    )


class ImageUploadView(View):
    form_class = ImageUploadForm
    template_name = 'admin/challenge/upload_image.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST, files=request.FILES)
        files = request.FILES.getlist('file_field')
        context = {}
        if form.is_valid():
            media_dir = pathlib.Path(settings.MEDIA_ROOT)
            urls = []
            for f in files:
                file_uuid = str(uuid.uuid1())
                filename = f"{file_uuid}.{f.name.split('.')[-1]}"
                file_path = media_dir / filename
                with open(file_path, 'wb') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)
                urls.append(f"/media/{filename}")
            context.update({'success': True, 'urls': urls})
        context.update({'form': form})
        return render(request, self.template_name, context)
