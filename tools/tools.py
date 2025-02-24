from langchain_community.tools.tavily_search import TavilySearchResults
#최적화된 검색 API


def get_profile_url_tavily(name: str):
    """Searches for Linkedin or twitter Profile Page."""
    print("here")
    search = TavilySearchResults()
    res = search.run(f"{name}")
    return res