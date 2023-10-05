from django import forms
from django.contrib import admin
from subsites.form import SubsiteAdminModelForm
from subsites.models import SubSite

@admin.register(SubSite)
class SubSiteAdmin(admin.ModelAdmin):
    form = SubsiteAdminModelForm

    filter_horizontal = (
        "region",
        "category",
        "keyword",
        "groups",
    )

