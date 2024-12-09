from datetime import datetime
from django.conf import settings
from django.http import Http404
from django.views.generic import TemplateView
from geonode.base.api.views import ResourceBaseViewSet
from geonode.people.api.views import UserViewSet
from geonode.documents.api.views import DocumentViewSet
from geonode.geoapps.api.views import GeoAppViewSet
from geonode.layers.api.views import DatasetViewSet
from geonode.maps.api.views import MapViewSet
from subsites import serializers
from subsites.utils import extract_subsite_slug_from_request, subsite_render
from django.shortcuts import redirect, render
from geonode.base.models import ResourceBase
from geonode.utils import resolve_object
from geonode.facets.views import ListFacetsView, GetFacetView
from geonode.base.models import HierarchicalKeyword
from distutils.util import strtobool


def subsite_home(request, subsite):
    slug = extract_subsite_slug_from_request(request, return_object=False)
    if not slug:
        response = render(request, "404.html")
        response.status_code = 404
        return response

    return subsite_render(request, "index.html", slug=slug)


def bridge_view(request, subsite, **kwargs):
    return kwargs["view"](request)

def embed_view(request, subsite, **kwargs):
    _view = kwargs.pop('view')
    pk = kwargs.pop('resourceid')
    return _view(request, pk, **kwargs)


def resolve_uuid(request, subsite, uuid):
    slug = extract_subsite_slug_from_request(request, return_object=False)
    if not slug:
        raise Http404(request, None)
    resource = resolve_object(request, ResourceBase, {"uuid": uuid})
    return redirect(f"/{slug}{resource.detail_url}")


# API viewset override for subsite


def retrieve_subsite_queryset(qr, request):
    subsite_obj = extract_subsite_slug_from_request(request)
    if not subsite_obj:
        return qr
    return subsite_obj.filter_by_subsite_condition(qr)


class SubsiteResourceBaseViewSet(ResourceBaseViewSet):
    serializer_class = serializers.SubsiteResourceBaseSerializer

    def get_queryset(self, queryset=None):
        qr = super().get_queryset(queryset)
        return retrieve_subsite_queryset(qr, self.request)


class SubsiteDatasetViewSet(DatasetViewSet):
    serializer_class = serializers.SubsiteDatasetSerializer

    def get_queryset(self, queryset=None):
        qr = super().get_queryset(queryset)
        return retrieve_subsite_queryset(qr, self.request)

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.SubsiteDatasetListSerializer
        return serializers.SubsiteDatasetSerializer


class SubsiteDocumentViewSet(DocumentViewSet):
    serializer_class = serializers.SubsiteDocumentSerializer

    def get_queryset(self, queryset=None):
        qr = super().get_queryset(queryset)
        return retrieve_subsite_queryset(qr, self.request)


class SubsiteGeoAppViewSet(GeoAppViewSet):
    serializer_class = serializers.SubsiteGeoAppSerializer

    def get_queryset(self, queryset=None):
        qr = super().get_queryset(queryset)
        return retrieve_subsite_queryset(qr, self.request)


class SubsiteMapViewSet(MapViewSet):
    serializer_class = serializers.SubsiteMapSerializer

    def get_queryset(self, queryset=None):
        qr = super().get_queryset(queryset)
        return retrieve_subsite_queryset(qr, self.request)


class SubsiteUserViewSet(UserViewSet):
    serializer_class = serializers.SubsiteUserSerializer


class SubsiteCatalogueViewSet(TemplateView):
    def get(self, request, *args, **kwargs):
        subsite = extract_subsite_slug_from_request(request)
        if subsite is None:
            raise Http404(request, None)
        context = self.get_context_data(**kwargs)
        slug = extract_subsite_slug_from_request(request, return_object=False)
        if not slug:
            raise Http404(request, None)
        return subsite_render(
            request, context["view"].template_name, context=context, slug=slug
        )


# Facets


class SubsiteListFacetsView(ListFacetsView):
    @classmethod
    def _prefilter_topics(cls, request):
        qr = super()._prefilter_topics(request)
        return retrieve_subsite_queryset(qr, request=request)


class SubsiteGetFacetView(GetFacetView):
    def get(self, request, subsite, facet):
        return super().get(request, facet)

    @classmethod
    def _prefilter_topics(cls, request):
        qr = super()._prefilter_topics(request)
        return retrieve_subsite_queryset(qr, request=request)


# Main API handling


class BaseKeywordExclusionMixin:

    def get_queryset(self, queryset=None):
        qr = super().get_queryset(queryset)
        try:
            return_all = strtobool(self.request.query_params.get("return_all", "None"))
            if return_all:
                return qr
        except Exception:
            pass
        k, _ = HierarchicalKeyword.objects.get_or_create(slug="subsite_exclusive")
        return qr.exclude(keywords__in=[k])


class OverrideResourceBaseViewSet(BaseKeywordExclusionMixin, ResourceBaseViewSet):
    pass


class OverrideDocumentViewSet(BaseKeywordExclusionMixin, DocumentViewSet):
    pass


class OverrideDatasetViewSet(BaseKeywordExclusionMixin, DatasetViewSet):
    pass


class OverrideMapViewSet(BaseKeywordExclusionMixin, MapViewSet):
    pass


class OverrideGeoAppViewSet(BaseKeywordExclusionMixin, GeoAppViewSet):
    pass
