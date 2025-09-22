from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults
import json

def query_ddg(question: str, is_img: bool):

    search = DuckDuckGoSearchResults(output_format='json', source="images" if is_img else "news")

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
