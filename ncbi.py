import os
from Bio import Entrez

Entrez.email = os.getenv("NCBI_EMAIL")
Entrez.api_key = os.getenv("NCBI_API_KEY")


def literature_search(
    query,
    database="pubmed",
    max_results=20
):
    """
    Search any NCBI literature database.
    Returns normalized results for Streamlit.
    """

    try:
        # Search database
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

        # Get summaries
        summary_handle = Entrez.esummary(
            db=database,
            id=",".join(ids)
        )

        summary_record = Entrez.read(summary_handle)
        summary_handle.close()

        results = []

        for item in summary_record:

            result = {
                "ID": str(item.get("Id", "")),
                "Title": str(item.get("Title", "")),
                "Journal": str(item.get("FullJournalName", "")),
                "Date": str(item.get("PubDate", "")),
            }

            results.append(result)

        return results

    except Exception as e:
        print(f"NCBI Error: {e}")
        return []
