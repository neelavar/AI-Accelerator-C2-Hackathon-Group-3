"""
Clients for external APIs like PubMed.
"""
import httpx
import xml.etree.ElementTree as ET
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from typing import List, Dict, Any
from langchain_core.documents import Document

class PubMedClient:
    """
    Client for interacting with the PubMed E-utilities API.
    """
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.client = httpx.AsyncClient()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry=retry_if_exception_type(httpx.RequestError)
    )
    async def _fetch_pubmed_ids(self, query: str, retmax: int = 10) -> List[str]:
        """
        Fetches PubMed IDs (PMIDs) for a given query using ESearch.
        """
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": retmax,
            "retmode": "json"
        }
        if self.api_key:
            params["api_key"] = self.api_key

        response = await self.client.get(f"{self.BASE_URL}esearch.fcgi", params=params)
        response.raise_for_status()
        data = response.json()
        
        # Handle potential missing data more gracefully
        try:
            return data.get("esearchresult", {}).get("idlist", [])
        except (KeyError, TypeError):
            print(f"Warning: Unexpected response format from PubMed: {data}")
            return []

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry=retry_if_exception_type(httpx.RequestError)
    )
    async def _fetch_article_details(self, pubmed_ids: List[str]) -> List[Document]:
        """
        Fetches details for a list of PubMed IDs using EFetch.
        """
        if not pubmed_ids:
            return []

        params = {
            "db": "pubmed",
            "id": ",".join(pubmed_ids),
            "retmode": "xml",
            "rettype": "abstract"
        }
        if self.api_key:
            params["api_key"] = self.api_key

        response = await self.client.get(f"{self.BASE_URL}efetch.fcgi", params=params)
        response.raise_for_status()
        
        # Parse XML response
        root = ET.fromstring(response.text)
        articles = []
        for article in root.findall(".//PubmedArticle"):
            pmid = article.find(".//PMID").text if article.find(".//PMID") is not None else "N/A"
            title = article.find(".//ArticleTitle").text if article.find(".//ArticleTitle") is not None else "No Title"
            abstract_elements = article.findall(".//AbstractText")
            abstract = "\n".join([p.text for p in abstract_elements if p.text]) if abstract_elements else "No Abstract"
            
            # Combine title and abstract for content
            content = f"Title: {title}\nAbstract: {abstract}"
            
            # Extract authors
            authors = []
            for author_element in article.findall(".//Author"):
                last_name = author_element.find("LastName").text if author_element.find("LastName") is not None else ""
                fore_name = author_element.find("ForeName").text if author_element.find("ForeName") is not None else ""
                authors.append(f"{fore_name} {last_name}".strip())
            authors_str = ", ".join(authors)

            # Extract publication date
            pub_date_element = article.find(".//PubDate")
            year = pub_date_element.find("Year").text if pub_date_element and pub_date_element.find("Year") is not None else "N/A"
            month = pub_date_element.find("Month").text if pub_date_element and pub_date_element.find("Month") is not None else "N/A"
            day = pub_date_element.find("Day").text if pub_date_element and pub_date_element.find("Day") is not None else "N/A"
            pub_date = f"{year}-{month}-{day}"

            metadata = {
                "source": f"PubMed (PMID: {pmid})",
                "pmid": pmid,
                "title": title,
                "authors": authors_str,
                "publication_date": pub_date,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            }
            articles.append(Document(page_content=content, metadata=metadata))
        return articles

    async def search(self, query: str, retmax: int = 10) -> List[Document]:
        """
        Performs a full search on PubMed, fetching IDs and then article details.
        """
        print(f"PubMedClient: Searching for query: '{query}'")
        pubmed_ids = await self._fetch_pubmed_ids(query, retmax)
        print(f"PubMedClient: Found {len(pubmed_ids)} PMIDs.")
        articles = await self._fetch_article_details(pubmed_ids)
        print(f"PubMedClient: Retrieved {len(articles)} articles.")
        return articles

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

# Example usage (for testing purposes)
async def main():
    client = PubMedClient()
    try:
        results = await client.search("COVID-19 treatment", retmax=2)
        for doc in results:
            print(f"---" " Article ---")
            print(f"Title: {doc.metadata['title']}")
            print(f"PMID: {doc.metadata['pmid']}")
            print(f"URL: {doc.metadata['url']}")
            print(f"Abstract: {doc.page_content[:200]}...") # Print first 200 chars of content
            print("\n")
    except httpx.RequestError as e:
        print(f"HTTP Request Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        await client.client.aclose()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
