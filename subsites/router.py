from collections import OrderedDict
from dynamic_rest import routers
from rest_framework import views
from rest_framework.response import Response


class SubSiteDynamicRouter(routers.DynamicRouter):
    def get_api_root_view(self, **kwargs):
        """Return API root view, using the global directory."""

        class API(views.APIView):
            _ignore_model_permissions = True

            def get(self, request, *args, **kwargs):
                directory_list = routers.get_directory(request)
                result = OrderedDict()
                subsite = kwargs.get("subsite", None)
                for group_name, url, endpoints, _ in directory_list:
                    if url:
                        if subsite:
                            result[group_name] = url.replace(
                                "/api/v2/", f"/{subsite}/api/v2/"
                            )
                        else:
                            result[group_name] = url
                    else:
                        group = OrderedDict()
                        for endpoint_name, url, _, _ in endpoints:
                            if subsite:
                                group[endpoint_name] = url.replace(
                                    "/api/v2/", f"/{kwargs.get('subsite')}/api/v2/"
                                )
                            else:
                                group[endpoint_name] = url
                        result[group_name] = group
                return Response(result)

        return API.as_view()
