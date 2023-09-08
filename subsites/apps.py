from django.apps import AppConfig
from django.urls import re_path


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
    from django.conf.urls import include
    from django.conf import settings
    from geonode.api.views import (admin_role, roles, user_info, users,
                                   verify_token)
    from geonode.base.api.urls import views as resourcebase_view
    from geonode.resource.api.views import ExecutionRequestViewset
    from geonode.urls import urlpatterns

    from subsites import views
    from subsites.router import SubSiteDynamicRouter

    router = SubSiteDynamicRouter()

    router.register(r"users", views.SubsiteUserViewSet, "users")
    router.register(r"groups", resourcebase_view.GroupViewSet, "group-profiles")
    router.register(r"resources", views.SubsiteResourceBaseViewSet, "base-resources")
    router.register(r"owners", resourcebase_view.OwnerViewSet, "owners")
    router.register(r"categories", resourcebase_view.TopicCategoryViewSet, "categories")
    router.register(r"keywords", resourcebase_view.HierarchicalKeywordViewSet, "keywords")
    router.register(r"tkeywords", resourcebase_view.ThesaurusKeywordViewSet, "tkeywords")
    router.register(r"regions", resourcebase_view.RegionViewSet, "regions")
    router.register(r"documents", views.SubsiteDocumentViewSet, "documents")
    router.register(r"geoapps", views.SubsiteGeoAppViewSet, "geoapps")
    router.register(r"datasets", views.SubsiteDatasetViewSet, "datasets")
    router.register(r"maps", views.SubsiteMapViewSet, "maps")
    router.register(r"executionrequest", ExecutionRequestViewset, "executionrequest")


    urlpatterns += [
        re_path(
            r"^(?P<subsite>[^/]*)/api/o/v4/tokeninfo",
            views.bridge_view,
            name="tokeninfo",
            kwargs={"view": verify_token},
        ),
        re_path(
            r"^(?P<subsite>[^/]*)/api/o/v4/userinfo",
            views.bridge_view,
            name="userinfo",
            kwargs={"view": user_info},
        ),
        # Api Views
        re_path(
            r"^(?P<subsite>[^/]*)/api/roles",
            views.bridge_view,
            name="roles",
            kwargs={"view": roles},
        ),
        re_path(
            r"^(?P<subsite>[^/]*)/api/adminRole",
            views.bridge_view,
            name="adminRole",
            kwargs={"view": admin_role},
        ),
        re_path(r"^(?P<subsite>[^/]*)/api/users", users, name="users"),
        re_path(r"^(?P<subsite>[^/]*)/api/v2/", include(router.urls)),
        re_path(r"^(?P<subsite>[^/]*)/api/v2/", include("geonode.api.urls")),
        re_path(
            r"^(?P<subsite>[^/]*)/catalogue/",
            views.SubsiteCatalogueViewSet.as_view(template_name="geonode-mapstore-client/catalogue.html"),
        ),
        re_path(r"^(?P<subsite>[^/]*)", views.subsite_home, name="subsite_home"),
    ]

    settings.TEMPLATES[0]["DIRS"].insert(0, os.path.join(settings.LOCAL_ROOT, "templates"))
    settings.CONTEXT_PROCESSORS += ["subsites.context_processors.custom_theme"]
