import os

from django.template import TemplateDoesNotExist
from django.template.backends.django import (DjangoTemplates, make_context,
                                             reraise)

from subsites import project_dir
from pathlib import Path
from subsites.utils import extract_subsite_slug_from_request
from django.template.loaders.filesystem import Loader


class SubsiteTemplateLoader(Loader):
    def get_contents(self, origin, custom_template_path=None):
        try:
            with open(custom_template_path or origin.name, encoding=self.engine.file_charset) as fp:
                return fp.read()
        except FileNotFoundError:
            raise TemplateDoesNotExist(origin)


class SubsiteTemplateBackend(DjangoTemplates):

    def __init__(self, params):
        super().__init__(params=params)

    def from_string(self, template_code):
        return CustomSubsiteTemplate(self.engine.from_string(template_code), self)

    def get_template(self, template_name):
        try:
            return CustomSubsiteTemplate(self.engine.get_template(template_name), self)
        except TemplateDoesNotExist as exc:
            reraise(exc, self)


class CustomSubsiteTemplate:

    def __init__(self, template, backend):
        self.template = template
        self.backend = backend

    @property
    def origin(self):
        return self.template.origin

    def render(self, context=None, request=None):
        context = make_context(context, request, autoescape=self.backend.engine.autoescape)
        slug = extract_subsite_slug_from_request(request, return_object=False)
        try:
            self.template.name = Path(self.template.name).name
            custom_template_path = f'{project_dir}/templates/{slug}/{self.template.name}'
            if slug and os.path.exists(custom_template_path):
                source = self.template.engine.template_loaders[0].get_contents(self.origin, custom_template_path)
                self.template.source = source
                
            return self.template.render(context)
        except TemplateDoesNotExist as exc:
            reraise(exc, self.backend)
