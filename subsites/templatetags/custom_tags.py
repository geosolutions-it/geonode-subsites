from django import template
from subsites.models import SubSite

from subsites.utils import extract_subsite_slug_from_request
from geonode_mapstore_client.templatetags.get_menu_json import (
    get_base_left_topbar_menu,
    get_user_menu,
    get_base_right_topbar_menu,
)
from django.conf import settings
from django.core.cache import caches

register = template.Library()


@register.simple_tag
def load_subsite_info(request):
    subsite = extract_subsite_slug_from_request(request)
    if not subsite:
        return None
    return subsite.slug

@register.simple_tag
def load_settings(lookup_value):
    return getattr(settings, lookup_value, None)


@register.simple_tag
def load_subsite_queryset():
    subsite_cache = caches["subsite_cache"]
    subsite_queryset = subsite_cache.get("subsite_queryset")
    if subsite_queryset:
        return subsite_queryset
    qr = SubSite.objects.all()
    subsite_cache.set("subsite_queryset", SubSite.objects.all(), 200)
    return qr


@register.simple_tag(takes_context=True)
def subsite_get_base_left_topbar_menu(context, request):
    result = get_base_left_topbar_menu(context)
    subsite = extract_subsite_slug_from_request(request)
    if subsite:
        result = _update_url_with_subsite(result, subsite)
    return result


@register.simple_tag(takes_context=True)
def subsite_get_user_menu(context, request):
    subsite = extract_subsite_slug_from_request(request)
    if subsite:
        return []
    return get_user_menu(context)


@register.simple_tag(takes_context=True)
def subsite_get_base_right_topbar_menu(context, request):
    subsite = extract_subsite_slug_from_request(request)
    if subsite:
        return []
    return get_base_right_topbar_menu(context)


# settings value
@register.simple_tag
def site_url():
    return getattr(settings, "SITEURL", "http://localhost:8000")


def _update_url_with_subsite(result, subsite):
    for element in result:
        if element.get("type", "") == "link":
            element["href"] = f"/{subsite}{element['href']}"
        elif element.get("items", ""):
            for item in element["items"]:
                if item.get("type", "") == "link":
                    item["href"] = f"/{subsite}{item['href']}"
    return result

@register.simple_tag(takes_context=True)
def subsite_catalogue_home(context):
    _path = ""
    if context and 'request' in context:
        current_path = context['request'].path
        subsite = extract_subsite_slug_from_request(context['request'])
        if current_path == '/':
            _path = "/"
        elif current_path.find('/catalogue') == 0:
            _path = "#"
        else:
            _path = "/catalogue/#"
        if subsite:
            return f"/{subsite}" + _path
    return _path
