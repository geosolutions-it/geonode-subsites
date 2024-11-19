from django.apps import AppConfig
from django.conf import settings
from django.urls import include, re_path


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "subsites"

    def ready(self):
        """Finalize setup"""
        run_setup_hooks()
        super(AppConfig, self).ready()
        post_ready_action()


def run_setup_hooks(*args, **kwargs):
    """
    Run basic setup configuration for the importer app.
    Here we are overriding the upload API url
    """
    import os

    LOCAL_ROOT = os.path.abspath(os.path.dirname(__file__))

    settings.TEMPLATES[0]["DIRS"].insert(0, os.path.join(LOCAL_ROOT, "templates"))
    settings.CONTEXT_PROCESSORS += [
        "subsites.context_processors.custom_theme",
        "subsites.context_processors.resource_urls",
    ]


def post_ready_action():

    from geonode.urls import urlpatterns
    from subsites.core_api import core_api_router

    urlpatterns += [re_path(r"", include("subsites.urls"))]
    urlpatterns.insert(
        0,
        re_path(r"^api/v2/", include(core_api_router.urls)),
    )
    settings.CACHES["subsite_cache"] = {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "TIMEOUT": 300,
        "OPTIONS": {"MAX_ENTRIES": 10000},
    }

    try:
        from geonode.base.models import HierarchicalKeyword
        HierarchicalKeyword.objects.get_or_create(name="subsite_exclusive", slug="subsite_exclusive", depth=1)
    except:
        pass
