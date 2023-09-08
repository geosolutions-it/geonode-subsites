from geonode.base.api.serializers import UserSerializer
from geonode.base.api.serializers import ResourceBaseSerializer
from subsites.utils import extract_subsite_slug_from_request
from geonode.documents.api.serializers import DocumentSerializer
from geonode.geoapps.api.serializers import GeoAppSerializer
from geonode.layers.api.serializers import DatasetSerializer, DatasetListSerializer
from geonode.maps.api.serializers import MapSerializer
from django.conf import settings


class SubsiteUserSerializer(UserSerializer):
    def to_representation(self, instance):
        # Dehydrate users private fields
        data = super().to_representation(instance)
        if data.get("perms") and settings.SUBSITE_READ_ONLY:
            data["perms"] = ["view_resourcebase"]
        return data


def apply_subsite_changes(data, request):
    subsite = extract_subsite_slug_from_request(request)
    data["detail_url"] = data["detail_url"].replace(
        "catalogue/", f"{subsite}/catalogue/"
    )
    if settings.SUBSITE_READ_ONLY:
        data["perms"] = ["view_resourcebase"]
    data["download_url"] = None
    return data


class SubsiteResourceBaseSerializer(ResourceBaseSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return apply_subsite_changes(data, self.context["request"])


class SubsiteDatasetSerializer(DatasetSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return apply_subsite_changes(data, self.context["request"])


class SubsiteDatasetListSerializer(DatasetListSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return apply_subsite_changes(data, self.context["request"])


class SubsiteDocumentSerializer(DocumentSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return apply_subsite_changes(data, self.context["request"])


class SubsiteMapSerializer(MapSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return apply_subsite_changes(data, self.context["request"])


class SubsiteGeoAppSerializer(GeoAppSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return apply_subsite_changes(data, self.context["request"])
