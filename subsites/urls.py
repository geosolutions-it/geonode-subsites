from django.conf.urls import include
from django.urls import path, re_path
from geonode.api.views import admin_role, roles, user_info, users, verify_token
from geonode.base.api.urls import views as resourcebase_view
from geonode.resource.api.views import ExecutionRequestViewset
from geonode.maps.views import map_embed
from geonode.documents.views import document_embed
from geonode.layers.views import dataset_embed
from geonode.geoapps.views import geoapp_edit

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

urlpatterns = [
    re_path(
        r"^(?P<subsite>[^/]*)/documents/(?P<resourceid>\d+)/embed/?$",
        views.embed_view,
        name="document_embed",
        kwargs={"view": document_embed},
    ),
    re_path(
        r"^(?P<subsite>[^/]*)/maps/(?P<resourceid>[^/]+)/embed$",
        views.embed_view,
        name="map_embed",
        kwargs={"view": map_embed},
    ),
    re_path(
        r"^(?P<subsite>[^/]*)/datasets/(?P<resourceid>[^/]+)/embed$",
        views.embed_view,
        name="dataset_embed",
        kwargs={"view": dataset_embed},
    ),
    re_path(
        r"^(?P<subsite>[^/]*)/apps/(?P<resourceid>[^/]+)/embed$",
        views.embed_view,
        name="geoapp_edit",
        kwargs={"view": geoapp_edit, "template": "apps/app_embed.html"},
    ),
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
    path(
        r"<str:subsite>/api/v2/facets/<facet>",
        views.SubsiteGetFacetView.as_view(),
        name="subsite_get_facet",
    ),
    re_path(
        r"^(?P<subsite>[^/]*)/api/v2/facets",
        views.SubsiteListFacetsView.as_view(),
        name="subsite_list_facets",
    ),
    re_path(r"^(?P<subsite>[^/]*)/api/users", users, name="users"),
    re_path(r"^(?P<subsite>[^/]*)/api/v2/", include(router.urls)),
    re_path(r"^(?P<subsite>[^/]*)/api/v2/", include("geonode.api.urls")),
    path(
        r"<str:subsite>/catalogue/uuid/<uuid:uuid>",
        views.resolve_uuid,
        name="subsite_resolve_uuid",
    ),
    re_path(
        r"^(?P<subsite>[^/]*)/catalogue/",
        views.SubsiteCatalogueViewSet.as_view(
            template_name="geonode-mapstore-client/catalogue.html"
        ),
        name="subsite_catalogue_root",
    ),
    re_path(r"^(?P<subsite>[^/]*)/$", views.subsite_home, name="subsite_home"),
]
