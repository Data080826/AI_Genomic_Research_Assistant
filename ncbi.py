import os
from Bio import Entrez
import pandas as pd

Entrez.email = os.getenv("NCBI_EMAIL")
Entrez.api_key = os.getenv("NCBI_API_KEY")

def search_pubmed(query, max_results=20):
    handle = Entrez.esearch(
        db="ncbi",
        term=query,
        retmax=max_results,
        sort="relevance"
    )

    results = Entrez.read(handle)
    handle.close()

    return results["IdList"]

from Bio import Medline

def fetch_ncbi_articles(pmids):

    ids = ",".join(pmids)

    handle = Entrez.efetch(
        db="ncbi",
        id=ids,
        rettype="medline",
        retmode="text"
    )

    records = Medline.parse(handle)

    articles = []

    for record in records:
        articles.append({
            "PMID": record.get("PMID", ""),
            "Title": record.get("TI", ""),
            "Journal": record.get("JT", ""),
            "Year": record.get("DP", ""),
            "Authors": record.get("AU", []),
            "Abstract": record.get("AB", "No abstract available")
        })

    handle.close()

    return articles

def literature_search(query, max_results=10):
    try:
        pmids = search_ncbi(query, max_results)

        if not pmids:
            return []

        return fetch_ncbi_articles(pmids)

    except Exception as e:
        print(f"NCBI error: {e}")
        return []



