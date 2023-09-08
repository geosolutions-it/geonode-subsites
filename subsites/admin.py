from django.contrib import admin
from subsites.models import SubSite


@admin.register(SubSite)
class SubSiteAdmin(admin.ModelAdmin):
    filter_horizontal = (
        "region",
        "category",
        "keyword",
    )
