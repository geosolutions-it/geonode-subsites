from geonode.people.api.serializers import UserSerializer
from geonode.base.api.serializers import ResourceBaseSerializer
from subsites.utils import extract_subsite_slug_from_request
from geonode.documents.api.serializers import DocumentSerializer
from geonode.geoapps.api.serializers import GeoAppSerializer
from geonode.layers.api.serializers import DatasetSerializer, DatasetListSerializer
from geonode.maps.api.serializers import MapSerializer
from django.conf import settings
from geonode.security.permissions import (
    _to_extended_perms,
    OWNER_RIGHTS,
)
from geonode.base.models import ResourceBase
import itertools
from rest_framework.exceptions import NotFound


class SubsiteUserSerializer(UserSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return apply_subsite_changes(data, self.context["request"], instance)


def apply_subsite_changes(data, request, instance):
    subsite = extract_subsite_slug_from_request(request)
    if not subsite:
        raise NotFound(detail="Subsite not found")
    if "detail_url" in data:
        data["detail_url"] = data["detail_url"].replace(
            "catalogue/", f"{subsite}/catalogue/"
        )
    # checking users perms based on the subsite_one
    if "perms" in data and isinstance(instance, ResourceBase):
        if getattr(settings, "SUBSITE_READ_ONLY", False):
            data["perms"] = ["view_resourcebase"]
            data["download_url"] = None
            data["download_urls"] = None
            return data

        owner = OWNER_RIGHTS in subsite.allowed_permissions
        # We expand the compact permission configured for the subsite
        # TODO: These could be precalculated and cached for performance
        subsite_allowed_perms = set(
            itertools.chain.from_iterable(
                filter(
                    None,
                    [
                        _to_extended_perms(
                            perm, instance.resource_type, instance.subtype, owner
                        )
                        for perm in subsite.allowed_permissions
                    ],
                )
            )
        )
        # We filter out the user permissions not included in subsite permissions
        user_allowed_perms = [
            perm for perm in data["perms"] if perm in subsite_allowed_perms
        ]
        data["perms"] = user_allowed_perms

        if "download_resourcebase" not in user_allowed_perms:
            data["download_url"] = None
            data["download_urls"] = None

    if not subsite.can_add_resource and data.get('perms', None):
        _perms_list = list(data['perms'])
        data['perms'] = [perm for perm in _perms_list if perm != 'add_resource']

    return data


class SubsiteResourceBaseSerializer(ResourceBaseSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return apply_subsite_changes(data, self.context["request"], instance)


class SubsiteDatasetSerializer(DatasetSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return apply_subsite_changes(data, self.context["request"], instance)


class SubsiteDatasetListSerializer(DatasetListSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return apply_subsite_changes(data, self.context["request"], instance)


class SubsiteDocumentSerializer(DocumentSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return apply_subsite_changes(data, self.context["request"], instance)


class SubsiteMapSerializer(MapSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return apply_subsite_changes(data, self.context["request"], instance)


class SubsiteGeoAppSerializer(GeoAppSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return apply_subsite_changes(data, self.context["request"], instance)
