
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


class SubsiteAdminModelForm(forms.ModelForm):

    def get_choices():
        resources = ResourceBase.objects.values_list('resource_type', 'subtype').distinct()
        subtypes = [
            (f"{_type[0]}__{_type[1]}", f"{_type[0]} - {_type[1]}".title())
            for _type in resources
            if _type[0] != 'map'
        ]
        resource_types = list(set([
            (_type[0], f"{_type[0]}".title())
            for _type in resources
        ]))
        return sorted(resource_types + subtypes, key=lambda x: x[1].split(" - ")[0])

    types = forms.MultipleChoiceField(
        choices=get_choices, widget=FilteredSelectMultiple(
            verbose_name="Resource types",
            is_stacked=False)
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if 'initial' not in kwargs:
            kwargs['initial'] = {}

        _initial = []
        for item in ast.literal_eval(kwargs.get("instance").types):
            _initial.extend([choice for choice in self.fields['types'].choices if item in choice[0]])
        #self.fields['types'].initial = _initial
        kwargs['initial'].update({'types': _initial})
    
    class Meta:
        model = SubSite
        fields = ("slug", "theme", "types", "region", "category", "keyword", "groups")

