import os
import requests

from custom_types import NodeInputVars

from .base_agent import BaseAgent


class WebSearchAgent(BaseAgent):
    def __init__(
        self,
        api_key: str = None,
        search_engine_id: str = None,
        num_results: int = 5,
        google_search_url: str = "https://www.googleapis.com/customsearch/v1",
    ):
        """Initialize the agent with config values from args or env variables."""
        # API KEYS, ENGINE ID not part of config for security and privacy
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.search_engine_id = search_engine_id or os.getenv("GOOGLE_CSE_ID")

        if not self.api_key or not self.search_engine_id:
            raise ValueError(
                "Missing API key or Search Engine ID. Set them via environment variables or arguments."
            )

        self.config = {
            "num_results": num_results,
            "google_search_url": google_search_url,
        }

    def execute(
        self, task: str, input_vars: NodeInputVars, output_vars: list[str], params: dict
    ) -> dict:
        """
        Execute the web search.
        """
        query = next(
            (var[1] for var in input_vars), ""
        )  # assuming input_vars is a list with single tuple ("query", query)
        config = self.config.copy()
        config.update(params)
        search_results = self._search_web(query, config)
        return {output_vars[0]: search_results}

    def _search_web(self, query: str, config: dict) -> dict:
        """
        Perform the web search using Google Custom Search API.

        Parameters:
        - query: The search query

        Returns:
        - dict: The web search results
        """
        params = {
            "q": query,
            "key": self.api_key,
            "cx": self.search_engine_id,
            "num": config["num_results"],
        }

        try:
            response = requests.get(config["google_search_url"], params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            search_results = response.json()
            return search_results["items"]
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}