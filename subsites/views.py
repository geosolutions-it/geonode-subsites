import os

from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView
from geonode.base.api.views import ResourceBaseViewSet, UserViewSet
from geonode.documents.api.views import DocumentViewSet
from geonode.geoapps.api.views import GeoAppViewSet
from geonode.layers.api.views import DatasetViewSet
from geonode.maps.api.views import MapViewSet

from subsites import project_dir, serializers
from subsites.utils import extract_subsite_slug_from_request


def subsite_home(request, subsite):
    slug = extract_subsite_slug_from_request(request)
    if not slug:
        raise Http404

    return render(request, "index.html")


def bridge_view(request, subsite, **kwargs):
    return kwargs["view"](request)


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
            raise Http404("Subsite does not exists")
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
