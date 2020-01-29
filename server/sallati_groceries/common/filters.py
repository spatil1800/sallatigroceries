from rest_framework.filters import SearchFilter


class CustomSearchFilter(SearchFilter):
    def get_search_terms(self, request):
        params = request.query_params.get(self.search_param, "")
        return params.split(", ")
