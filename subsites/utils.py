from django.conf import settings
from django.shortcuts import get_object_or_404

from subsites.models import SubSite


def extract_subsite_slug_from_request(request, return_object=True):
    """
    Return the Subsite object or None if not exists or not Enabled
    """
    if getattr(settings, "ENABLE_SUBSITE_CUSTOM_THEMES", False):
        url = request.path.split("/")
        split_path = list(filter(None, url))
        if split_path:
            subsite_name = split_path[0]
            try:
                x = SubSite.objects.filter(slug=subsite_name)
                if x.exists():
                    if return_object:
                        return x.first()
                    else:
                        return subsite_name
                return None
            except Exception:
                return None
    return None
