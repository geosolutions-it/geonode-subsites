import ast
from collections.abc import Mapping
from typing import Any
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from geonode.base.models import ResourceBase
from subsites.models import SubSite
from django.contrib.admin.widgets import FilteredSelectMultiple
from geonode.base.enumerations import LAYER_TYPES
from geonode.documents.enumerations import DOCUMENT_TYPE_MAP
from django.conf import settings


class SubsiteAdminModelForm(forms.ModelForm):
    def get_choices():
        resource_types = [
            ("dataset", "Dataset"),
            ("document", "Document"),
            ("map", "Maps"),
            ("geoapp", "GeoApp")
        ]

        subtypes = [
            (f"dataset__{x}", f"Dataset - {x.title()}") for x in LAYER_TYPES
        ] + [
            (f"document__{x}", f"Document - {x.title()}")
            for x in (
                set(settings.ALLOWED_DOCUMENT_TYPES + list(DOCUMENT_TYPE_MAP.values()))
            )
        ] + [
            (f"geoapp__{x}", f"GeoApp - {x.title()}")
            for x in settings.CLIENT_APP_LIST
        ]

        return sorted(resource_types + subtypes, key=lambda x: x[1].split(" - ")[0])

    types = forms.MultipleChoiceField(
        choices=get_choices,
        widget=FilteredSelectMultiple(verbose_name="Resource types", is_stacked=False),
    )

    class Meta:
        model = SubSite
        fields = ("slug", "theme", "types", "region", "category", "keyword", "groups")
