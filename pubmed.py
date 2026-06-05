from Bio import Entrez

Entrez.email = "your_email@example.com"

def search_pubmed(query, max_results=20):
    handle = Entrez.esearch(
        db="pubmed",
        term=query,
        retmax=max_results,
        sort="relevance"
    )

    results = Entrez.read(handle)
    handle.close()

    return results["IdList"]

from Bio import Medline

def fetch_pubmed_articles(pmids):

    ids = ",".join(pmids)

    handle = Entrez.efetch(
        db="pubmed",
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
            "Abstract": record.get("AB", "")
        })

    handle.close()

    return articles

def literature_search(query, max_results=10):

    pmids = search_pubmed(query, max_results)

    if not pmids:
        return []

    return fetch_pubmed_articles(pmids)

papers = literature_search(
    "BRCA1 breast cancer mutation",
    max_results=5
)

for paper in papers:
    print(paper["Title"])

