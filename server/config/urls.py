from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path
from django.views import defaults as default_views
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

SchemaView = get_schema_view(
    openapi.Info(
        title="Pure Storage API",
        default_version="v1",
        description="""Pure Storage API's
            The `swagger-ui` view can be found [here](/swagger).
            The `ReDoc` view can be found [here](/redoc).
            The swagger YAML document can be found [here](/swagger.yaml).
            """,
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
                  re_path(
                      r"^swagger(?P<format>\.json|\.yaml)$",
                      SchemaView.without_ui(cache_timeout=None),
                      name="schema-json",
                  ),
                  re_path(
                      r"^docs$",
                      SchemaView.with_ui("swagger", cache_timeout=None),
                      name="schema-swagger-ui",
                  ),
                  re_path(
                      r"^redoc$", SchemaView.with_ui("redoc", cache_timeout=None), name="schema-redoc"
                  ),
                  # path(
                  #     "v1/", include("sallati_groceries.accounts.urls", namespace="users")
                  # ),  # User management
                  # path(
                  #     "v1/", include("sallati_groceries.core.urls", namespace="core")
                  # ),  # Core logic APIs,
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
