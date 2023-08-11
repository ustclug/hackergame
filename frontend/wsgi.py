try:
    import gevent.monkey
    gevent.monkey.patch_all()
    import psycogreen.gevent
    psycogreen.gevent.patch_psycopg()
except ImportError:
    print("gevent or psycogreen not found, not patching")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
