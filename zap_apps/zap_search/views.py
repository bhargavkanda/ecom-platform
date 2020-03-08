from django.utils.datastructures import OrderedSet
from zap_apps.account.zapauth import ZapView
from zap_apps.zap_analytics.models import SearchAnalytics
from zap_apps.zap_search.search_result_helpers import get_search_results
from zap_apps.zap_search.suggestion_helpers import get_suggestions

SEARCH_HISTORY_LENGTH = 5


class Search(ZapView):

    """
    Get search Results\n
    First argument defines the type of search results\n
    e.g.
        POST /search/product - Search Results are products, in a feed

    **Request**

        Request Object Structure:

    **Response**

        Response Object Structure:

    """

    def post(self, request, result_type, product_type=None, format=None):
        try:
            # import pdb
            # pdb.set_trace()
            result = get_search_results(request, result_type, product_type)
            return self.send_response(1, result)

        except Exception as e:
            return self.send_response(0, {'error': e})


class Suggestions(ZapView):
    """
        Get search suggestions for the user while typing\n
        First argument defines the suggestions tab\n
        e.g.
            POST /search/suggestions/product - Provides string suggestions to filter products, and suggests products
            that have matches to the title and description\n
            POST /search/suggestion/closet - Provides suggestions for users that have matches to name and description


        **Request**
            Request Object Structure:

            Same for all suggestion tabs
            Dictionary with following fields:

                applied_filter
                    Filter selected by user at any stage - gets updated from response filters, whenever
                    user selects or auto-fills using one of the filters

                    Dictionary with product attributes as keys, and lists as values :

                    Category : []
                    SubCategory : []
                    Style : []
                    Color : []
                    Brand : []
                    Occasion : []

                query_string
                    String typed in by user that is not part of any applied filter

        **Response**
            Response Object Structure:

            For Products tab :




        """

    def post(self, request, suggestion_tab, format=None):
        try:
            all_suggestions = get_suggestions(request, suggestion_tab)
            return self.send_response(1, all_suggestions)

        except Exception as e:
            return self.send_response(0, {'error': e})



class SearchHistory(ZapView):

    def get(self, request, format=None):
        search_queries = list(OrderedSet([q[0] for q in SearchAnalytics.objects.filter(user=request.user).order_by(
            '-time').values_list('search_query')]))[:SEARCH_HISTORY_LENGTH]
        return self.send_response(1, search_queries)