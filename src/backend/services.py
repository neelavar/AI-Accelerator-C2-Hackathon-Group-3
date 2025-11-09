"""
External API client for PubMed and other services.
"""
import requests
from typing import List, Dict

class PubMedClient:
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    def search(self, query: str, api_key: str = None, retmax: int = 5) -> List[Dict]:
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": retmax,
            "retmode": "json"
        }
        if api_key:
            params["api_key"] = api_key
        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        return response.json()

def test_pubmed_search():
    client = PubMedClient()
    result = client.search("cancer")
    print(result)

if __name__ == "__main__":
    test_pubmed_search()
