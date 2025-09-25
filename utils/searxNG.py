import os 
import json
from langchain_community.utilities import SearxSearchWrapper


def query_searxng(question: str):
    search = SearxSearchWrapper(searx_host=os.getenv("SEARX_HOST"))

    search_results = search.results(question, num_results=10)

    if not search_results:
        return  {
            "success": False,
            "message": "Sorry, I couldn't find any recent news on that topic."
        }

    return {
        "success": True,
        "message": search_results
    }
