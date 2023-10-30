import logging

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple
from geonode.base.enumerations import LAYER_TYPES
from geonode.security import permissions

from subsites.models import SubSite

logger = logging.getLogger("geonode")

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
        help_text=(
            "Max allowed permissions that the users who vistis the subsite will have."
            "If no permissions are selected, view and download are automatically assigned."
            "NOTE: no additional permissions are added to the user"
        )
    )

    class Meta:
        model = SubSite
        fields = ("slug", "theme", "logo", "description", "types", "region", "category", "keyword", "groups")

    def save(self, commit=True):
        super().save(commit=commit)
        if not self.instance.allowed_permissions:
            logger.warning("No permissions set, at least view and download are automatically assigned")
            self.instance.allowed_permissions = ['view', 'download']
            self.instance.save()
        return self.instance
