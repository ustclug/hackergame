import logging
import os

from django.conf import settings
from django.core import mail
from django.utils.timezone import now
from django.utils.log import AdminEmailHandler


class ThrottledAdminEmailHandler(AdminEmailHandler):
    def send_mail(self, subject, message, *args, **kwargs):
        try:
            d = settings.MEDIA_ROOT + '/admin_email_throttle'
            try:
                try:
                    os.mkdir(settings.MEDIA_ROOT)
                except FileExistsError:
                    pass
                os.mkdir(d)
            except FileExistsError:
                pass
            t = now().isoformat()
            prefix = t[:16]
            count = 0
            for i in os.listdir(d):
                if i.startswith(prefix):
                    count += 1
                else:
                    try:
                        os.remove(d + '/' + i)
                    except FileNotFoundError:
                        pass
            if count < 5:
                with open(d + '/' + t, 'w'):
                    pass
                mail.mail_admins(subject, message, *args, connection=self.connection(), **kwargs)
        except Exception as e:
            mail.mail_admins(f'{subject} - {type(e)}: {e}', message, *args, connection=self.connection(), **kwargs)


class UserInfoFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, 'request'):
            try:
                record.userid = "user-" + str(record.request.user.id)
            except AttributeError:
                # 'WSGIRequest' object has no attribute 'user'
                record.userid = "user-unknown"
            record.ip = record.request.META.get('REMOTE_ADDR')
        return True
