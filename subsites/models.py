from django.db import models
from geonode.themes.models import GeoNodeThemeCustomization
from geonode.base.models import Region, HierarchicalKeyword, TopicCategory, GroupProfile
from django.db.models import Q


class SubSite(models.Model):
    slug = models.SlugField(
        verbose_name="Site name",
        max_length=250,
        null=False,
        blank=False,
        help_text="Sub site name, formatted as slug. This slug is going to be used as path for access the subsite",
    )
    theme = models.ForeignKey(
        GeoNodeThemeCustomization, on_delete=models.SET_NULL, null=True
    )

    region = models.ManyToManyField(Region, null=True, blank=True, default=None)
    category = models.ManyToManyField(
        TopicCategory, null=True, blank=True, default=None
    )
    keyword = models.ManyToManyField(
        HierarchicalKeyword, null=True, blank=True, default=None
    )
    groups = models.ManyToManyField(GroupProfile, null=True, blank=True, default=None)

    def __str__(self) -> str:
        return self.slug

    def filter_by_subsite_condition(self, qr):
        """
        Filter any input input resource queryset (resources, doc, map, dataset, geoapp)
        using the region, category and keyword filter defined.
        Only the resources matching the filter will be returned by default
        """
        _region_filter = self._define_or_filter(
            "regions", list(self.region.values_list("id", flat=True))
        )
        _category_filter = self._define_or_filter(
            "category", list(self.category.values_list("id", flat=True))
        )
        _keyword_filter = self._define_or_filter(
            "keywords", list(self.keyword.values_list("id", flat=True))
        )
        _group_filter = self._define_or_filter(
            "group", list(self.groups.values_list("id", flat=True))
        )

        return (
            qr.filter(_region_filter)
            .filter(_category_filter)
            .filter(_keyword_filter)
            .filter(_group_filter)
        )

    def _define_or_filter(self, key, iterable):
        match key:
            case "regions":
                queries = [Q(regions=value) for value in iterable]
                if not queries:
                    query = Q(regions=None)
            case "category":
                queries = [Q(category=value) for value in iterable]
                if not queries:
                    query = Q(category=None)
            case "keywords":
                queries = [Q(keywords=value) for value in iterable]
                if not queries:
                    query = Q(keywords=None)
            case "group":
                queries = [Q(group__groupprofile=value) for value in iterable]
                if not queries:
                    query = Q(group__groupprofile=None)
            case _:
                return None
        if not queries:
            return query
        query = queries.pop()
        for item in queries:
            query |= item
        return query
