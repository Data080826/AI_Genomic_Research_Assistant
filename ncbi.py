import os
from Bio import Entrez
import pandas as pd

Entrez.email = os.getenv("NCBI_EMAIL")
Entrez.api_key = os.getenv("NCBI_API_KEY")


def literature_search(
    query,
    database="pubmed",
    max_results=20
):
    """
    Search any NCBI Entrez literature database.
    """

    search_handle = Entrez.esearch(
        db=database,
        term=query,
        retmax=max_results
    )

    search_record = Entrez.read(search_handle)
    search_handle.close()

    ids = search_record["IdList"]

    if not ids:
        return []

    summary_handle = Entrez.esummary(
        db=database,
        id=",".join(ids)
    )

    summary_record = Entrez.read(summary_handle)
    summary_handle.close()

    papers = []

    for item in summary_record:

        papers.append(
            {
                "ID": item.get("Id", ""),
                "Title": item.get("Title", ""),
                "Journal": item.get("FullJournalName", ""),
                "PubDate": item.get("PubDate", "")
            }
        )

    return papers
