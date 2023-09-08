from django.conf import settings
from django.shortcuts import get_object_or_404

from subsites.models import SubSite


def extract_subsite_slug_from_request(request):
    """
    Return the Subsite object or None if not exists or not Enabled
    """
    if getattr(settings, "ENABLE_SUBSITE_CUSTOM_THEMES", False):
        url = request.path.split("/")
        split_path = list(filter(None, url))
        if split_path:
            subsite_name = split_path[0]
            try:
                return get_object_or_404(SubSite, slug=subsite_name)
            except Exception:
                return None
    return None
