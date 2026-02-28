from django.urls import path

from search.views import home, htmx_map_payload, htmx_results_partial, search_results

app_name = "search"

urlpatterns = [
    path("", home, name="home"),
    path("search", search_results),
    path("search/", search_results, name="results"),
    path("hx/search/results", htmx_results_partial),
    path("hx/search/results/", htmx_results_partial, name="hx_results"),
    path("hx/search/map", htmx_map_payload),
    path("hx/search/map/", htmx_map_payload, name="hx_map"),
]
