from django.contrib import admin
from subsites.models import SubSite


@admin.register(SubSite)
class SubSiteAdmin(admin.ModelAdmin):
    fields = ('slug', 'theme', 'resource_type', "region", "category", "keyword", "groups")
    filter_horizontal = (
        "region",
        "category",
        "keyword",
        "groups",
    )
