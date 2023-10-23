from django import forms
from subsites.models import SubSite
from django.contrib.admin.widgets import FilteredSelectMultiple
from geonode.base.enumerations import LAYER_TYPES
from django.conf import settings
from geonode.security import permissions


class SubsiteAdminModelForm(forms.ModelForm):
    def get_choices():
        resource_types = [
            ("dataset", "Dataset"),
            ("document", "Document"),
            ("map", "Maps"),
            ("geoapp", "GeoApp"),
        ]

        subtypes = [
            (f"dataset__{x}", f"Dataset - {x.title()}") for x in LAYER_TYPES
        ] + [(f"{x}", f"GeoApp - {x.title()}") for x in settings.CLIENT_APP_LIST]

        return sorted(resource_types + subtypes, key=lambda x: x[1].split(" - ")[0])

    types = forms.MultipleChoiceField(
        choices=get_choices,
        required=False,
        widget=FilteredSelectMultiple(verbose_name="Resource types", is_stacked=False),
    )

    allowed_permissions = forms.MultipleChoiceField(
        choices=permissions.COMPACT_RIGHT_MODES,
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name="Allowed Permissions", is_stacked=False
        ),
    )

    class Meta:
        model = SubSite
        fields = ("slug", "theme", "types", "region", "category", "keyword", "groups")
