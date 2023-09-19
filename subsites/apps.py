from django.apps import AppConfig
import urllib.parse


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "subsites"
    def ready(self):
        """Finalize setup"""
        run_setup_hooks()
        super(AppConfig, self).ready()


def run_setup_hooks(*args, **kwargs):
    """
    Run basic setup configuration for the importer app.
    Here we are overriding the upload API url
    """
    
    # from geonode.api.urls import router
    import os
    from django.conf import settings
    from geonode.urls import urlpatterns
    from subsites.urls import urlpatterns as subsite_url_patterns

    urlpatterns += subsite_url_patterns
    LOCAL_ROOT = os.path.abspath(os.path.dirname(__file__))

    settings.TEMPLATES[0]["DIRS"].insert(0, os.path.join(LOCAL_ROOT, "templates"))
    settings.TEMPLATES[0]["OPTIONS"].update({"loaders": ["subsites.custom_template.SubsiteTemplateLoader", "django.template.loaders.filesystem.Loader", "django.template.loaders.app_directories.Loader"]})
    settings.TEMPLATES[0]["BACKEND"] = "subsites.custom_template.SubsiteTemplateBackend"    
    settings.CONTEXT_PROCESSORS += ["subsites.context_processors.custom_theme"]
