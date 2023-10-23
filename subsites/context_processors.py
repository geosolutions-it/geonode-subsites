#########################################################################
#
# Copyright (C) 2023 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################
from django.conf import settings
from subsites.utils import extract_subsite_slug_from_request
from geonode.themes.context_processors import custom_theme as geonode_custom_theme
from geonode_mapstore_client.context_processors import (
    resource_urls as geonode_resource_urls,
)
from django.shortcuts import reverse


def custom_theme(request, *args, **kwargs):
    custom_theme_payload = geonode_custom_theme(request)
    subsite_obj = extract_subsite_slug_from_request(request)
    if getattr(settings, "ENABLE_SUBSITE_CUSTOM_THEMES", False):
        if subsite_obj:
            theme = subsite_obj.theme
            if theme:
                slides = theme.jumbotron_slide_show.filter(is_enabled=True)
                theme.is_enabled = True
                custom_theme_payload = {
                    "custom_theme": theme or {},
                    "slides": slides if slides.exists() else [],
                }
    if subsite_obj:
        custom_theme_payload["slug"] = subsite_obj.slug

    return custom_theme_payload


def resource_urls(request):
    geonode_urls = geonode_resource_urls(request=request)
    if getattr(settings, "ENABLE_CATALOG_HOME_REDIRECTS_TO", False):
        geonode_urls["GEONODE_SETTINGS"]["CATALOG_HOME_REDIRECTS_TO"] = None
        if request.resolver_match.url_name == "subsite_catalogue_root":
            geonode_urls["GEONODE_SETTINGS"]["CATALOG_HOME_REDIRECTS_TO"] = reverse(
                "subsite_home", kwargs=request.resolver_match.kwargs
            )
    return geonode_urls
