from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import TemplateDoesNotExist
from django.core.exceptions import ImproperlyConfigured

from subsites.models import SubSite


def extract_subsite_slug_from_request(request, return_object=True):
    """
    Return the Subsite object or None if not exists or not Enabled
    """
    if getattr(settings, "ENABLE_SUBSITE_CUSTOM_THEMES", False) and request is not None:
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


def subsite_get_template(template_name, using=None, slug=None):
    """
    Load and return a template for the given name.

    Raise TemplateDoesNotExist if no such template exists.
    """
    from subsites import project_dir
    from django.template.backends.django import DjangoTemplates
    _path = f"{project_dir}/templates/{slug}/"
    payload = {}
    options = subsite_get_settings()
    for template in options:
        if template == 'GeoNode Project Templates':
            payload = options[template].copy()
            break

    payload.pop('BACKEND')
    payload['DIRS'].insert(0, _path)

    engine = DjangoTemplates(payload)

    return engine.get_template(template_name)


def subsite_render_to_string(template_name, context=None, request=None, using=None, slug=None):
    """
    Load a template and render it with a context. Return a string.

    template_name may be a string or a list of strings.
    """
    template = subsite_get_template(template_name, using=using, slug=slug)
    return template.render(context, request)



def subsite_render(request, template_name, context=None, content_type=None, status=None, using=None, slug=None):
    """
    Return a HttpResponse whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    """

    content = subsite_render_to_string(template_name, context, request, using=using, slug=slug)
    return HttpResponse(content, content_type, status)


def subsite_get_settings():
    _templates = settings.TEMPLATES
    templates = {}
    for tpl in _templates:
        try:
            # This will raise an exception if 'BACKEND' doesn't exist or
            # isn't a string containing at least one dot.
            default_name = tpl['BACKEND'].rsplit('.', 2)[-2]
        except Exception:
            invalid_backend = tpl.get('BACKEND', '<not defined>')
            raise ImproperlyConfigured(
                "Invalid BACKEND for a template engine: {}. Check "
                "your TEMPLATES setting.".format(invalid_backend))

        tpl = {
            'NAME': default_name,
            'DIRS': [],
            'APP_DIRS': False,
            'OPTIONS': {},
            **tpl,
        }
        templates[tpl['NAME']] = tpl

    return templates