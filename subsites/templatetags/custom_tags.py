from django import template

from subsites.utils import extract_subsite_slug_from_request
from geonode_mapstore_client.templatetags.get_menu_json import (
    get_base_left_topbar_menu,
    get_user_menu,
    get_base_right_topbar_menu,
)
from django.conf import settings

register = template.Library()


@register.simple_tag
def load_subsite_info(request):
    subsite = extract_subsite_slug_from_request(request)
    if not subsite:
        return None
    return subsite.slug


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
