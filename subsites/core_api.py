from subsites import views
from dynamic_rest import routers

core_api_router = routers.DynamicRouter()


core_api_router.register(
    r"resources", views.OverrideResourceBaseViewSet, "base-resources"
)
core_api_router.register(r"documents", views.OverrideDocumentViewSet, "documents")
core_api_router.register(r"datasets", views.OverrideDatasetViewSet, "datasets")
core_api_router.register(r"maps", views.OverrideMapViewSet, "maps")
core_api_router.register(r"geoapps", views.OverrideGeoAppViewSet, "geoapps")
