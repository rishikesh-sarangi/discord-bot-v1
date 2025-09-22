from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults
import json

def query_ddg(question: str):
    search_wrapper = DuckDuckGoSearchAPIWrapper(    
        max_results=10
    )

    search = DuckDuckGoSearchResults(api_wrapper = search_wrapper, output_format='json')

    search_results = search.invoke(question)

    if not search_results:
        return  {
            "success": False,
            "message": "Sorry, I couldn't find any recent news on that topic."
        }

    return {
        "success": True,
        "message": json.loads(search_results)
    }
