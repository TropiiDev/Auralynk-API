import os
import json

from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

def search_youtube(query):
    """Search YouTube using Google and return the first video URL."""
    params = {
        "engine": "youtube",
        "search_query": query,
        "api_key": SERPAPI_API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    videos = results.get("video_results", [])

    if videos:
        return videos[0]  # Return the first YouTube video link
    else:
        return {"url": "No video found."}