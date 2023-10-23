import os
from copy import deepcopy
from django.conf import settings
from django.http import HttpResponse
from django.core.exceptions import ImproperlyConfigured
from subsites import project_dir
from django.template.backends.django import DjangoTemplates
from subsites.models import SubSite
from django.core.cache import caches

subsite_cache = caches["subsite_cache"]


def extract_subsite_slug_from_request(request, return_object=True):
    """
    Return the Subsite object or None if not exists or not Enabled
    """
    if getattr(settings, "ENABLE_SUBSITE_CUSTOM_THEMES", False) and request is not None:
        url = request.path.split("/")
        split_path = list(filter(None, url))
        if split_path:
            subsite_name = split_path[0]
            cached_value = subsite_cache.get(subsite_name)
            if cached_value:
                if return_object:
                    return cached_value
                else:
                    return subsite_name
            else:
                try:
                    x = SubSite.objects.filter(slug=subsite_name)
                    if x.exists():
                        subsite_cache.set(subsite_name, x.first(), 300)
                        if return_object:
                            return x.first()
                        else:
                            return subsite_name
                    return None
                except Exception:
                    return None
    return None


def subsite_render_to_string(
    template_name, context=None, request=None, using=None, slug=None
):
    """
    Dynamically load the template from the subsite template folder.
    A new "engine" object is initilized and the template directory for
    the single subsite is injected to the template engine can find
    the proper subsite-template.
    The engine is going to be initilized everytime so that
    we can dynamically load the subsite template.
    The subsite template structure must match the default geonode one
    """
    # creating the subsite template path
    _project_path = f"{settings.LOCAL_ROOT}/templates/subsites/{slug}/"
    _project_common_path = f"{settings.LOCAL_ROOT}/templates/subsites/common/"
    payload = {}
    # retrieve the settings information
    options = subsite_get_settings()
    # we want to use ONLY the default geonode template
    # then we can copy the params from it to init the template engine
    for template in options:
        if template == "GeoNode Project Templates":
            payload = deepcopy(options[template])
            break
    # the key backend is not needed so we pop it out
    payload.pop("BACKEND")
    # if the subsite template path exsits, we will add it
    # as first in the template dir lists so it will match during
    # the  rendering
    _paths = [_project_common_path, _project_path]
    for _single_path in _paths:
        if os.path.exists(_single_path):
            payload["DIRS"].insert(0, _single_path)

    # we initiate the Template Engine with the above payload
    engine = DjangoTemplates(payload)

    template = engine.get_template(template_name)

    # after getting the template, we can finally render it
    # the subsite template will match since is first in the dirs order
    return template.render(context, request)


def subsite_render(
    request,
    template_name,
    slug,
    context=None,
    content_type=None,
    status=None,
    using=None,
):
    """
    Used instead of the default django render function.
    This is needed since we can dynamically load the subsite
    template based on the request coming from the view
    It will return the HttpResponse with the template
    for the selected subsite
    """
    content = subsite_render_to_string(
        template_name, context, request, using=using, slug=slug
    )
    return HttpResponse(content, content_type, status)


def subsite_get_settings():
    """
    Mock of the django function used during the startup
    to initialize the template engines.
    The function will read the settings.TEMPLATE variable
    and generates a payload with all the information needed
    to successfully load the template (context processors, app_dirs) etc...
    """
    _templates = settings.TEMPLATES
    templates = {}
    for tpl in _templates:
        try:
            # This will raise an exception if 'BACKEND' doesn't exist or
            # isn't a string containing at least one dot.
            default_name = tpl["BACKEND"].rsplit(".", 2)[-2]
        except Exception:
            invalid_backend = tpl.get("BACKEND", "<not defined>")
            raise ImproperlyConfigured(
                "Invalid BACKEND for a template engine: {}. Check "
                "your TEMPLATES setting.".format(invalid_backend)
            )

        tpl = {
            "NAME": default_name,
            "DIRS": [],
            "APP_DIRS": False,
            "OPTIONS": {},
            **tpl,
        }
        templates[tpl["NAME"]] = tpl
    # return a payload with the default geonode project template
    # and all the default context_processors, app_dirs etc...
    # required for load the template
    return templates
