import streamlit as st
import pandas as pd
from Bio import SeqIO
from openai import OpenAI
from ncbi import literature_search

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="GenomeGPT",
    page_icon="🧬",
    layout="wide"
)

# -----------------------------------
# SESSION STATE
# -----------------------------------

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False
    
if "api_key_active" not in st.session_state:
    st.session_state.api_key_active = None

# -----------------------------------
# TITLE
# -----------------------------------

st.title("🧬 GenomeGPT")
st.subheader("AI-Powered Genomic Research Assistant")

# -----------------------------------
# SIDEBAR
# -----------------------------------

with st.sidebar:

    st.title("GenomeGPT")
  

    # -----------------------------------
    # USER API KEY
    # -----------------------------------

    st.markdown("""
    Enter your OpenAI API key
    to enable Real AI responses
    """)

    with st.form("api_key_form"):

        user_api_key = st.text_input(
            "",
            type="password",
            placeholder="sk-...",
            help="Your API key is never stored"
        )

        submitted = st.form_submit_button(
            "🔑 Activate API Key"
        )

        if submitted:

            if not user_api_key:

                st.warning(
                    "Please enter an API key."
                )

            else:

                st.session_state.api_key_active = (
                    user_api_key
                )

                st.success(
                    "API Key Activated"
                )

    if st.session_state.api_key_active:

        st.success(
            "🟢 OpenAI Connected"
        )

        if st.button(
            "❌ Disconnect API Key"
        ):

            st.session_state.api_key_active = None
            st.rerun()

    else:

        st.info(
            "🔴 OpenAI Not Connected"
        )

    st.markdown(
        "[Get your API key from OpenAI Platform](https://platform.openai.com/api-keys)"
    )

    st.write("---")

    # -----------------------------------
    # HIDDEN ADMIN ACCESS
    # -----------------------------------

    admin_access = st.text_input(
        "Admin Access",
        type="password",
        placeholder="Hidden"
    )

    # -----------------------------------
    # ADMIN AUTH
    # -----------------------------------

    if (
        admin_access
        and admin_access == st.secrets["ADMIN_PASSWORD"]
    ):
        st.session_state.admin_authenticated = True

    # -----------------------------------
    # ADMIN CONTROLS
    # -----------------------------------

    if st.session_state.admin_authenticated:

        st.success("✅ Admin Mode Enabled")

        if st.button("Logout Admin"):

            st.session_state.admin_authenticated = False
            st.rerun()

    else:

        st.caption("🌐 Public Research Demo")
# -----------------------------------
# OPENAI CLIENT
# -----------------------------------

client = None

if st.session_state.api_key_active:

    try:

        client = OpenAI(
            api_key=(
                st.session_state.api_key_active
            )
        )

    except Exception as e:

        st.error(
            f"OpenAI Error: {e}"
        )
# -----------------------------------
# STATUS
# -----------------------------------

if st.session_state.api_key_active:

    st.success(
        "🤖 Real AI Mode Active"
    )

else:

    st.info(
        "🧪 Demo Mode Active • Connect an API key to use Real AI."
    )
# -----------------------------------
# FILE UPLOAD
# -----------------------------------

uploaded_file = st.file_uploader(
    "Upload genomic dataset",
    type=["csv", "vcf", "txt", "fasta", "fa"]
)

file_content = ""

# -----------------------------------
# FILE PROCESSING
# -----------------------------------

if uploaded_file:

    st.success(f"Uploaded: {uploaded_file.name}")

    try:

        # -----------------------------------
        # CSV FILES
        # -----------------------------------

        if uploaded_file.name.endswith(".csv"):

            df = pd.read_csv(uploaded_file)

            st.write("### Dataset Preview")
            st.dataframe(df.head())

            st.write("### Dataset Statistics")

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Rows", df.shape[0])

            with col2:
                st.metric("Columns", df.shape[1])

            st.write("### Columns")
            st.write(df.columns.tolist())

            file_content = df.head(25).to_string()

        # -----------------------------------
        # FASTA FILES
        # -----------------------------------

        elif uploaded_file.name.endswith((".fasta", ".fa")):

            sequences = list(
                SeqIO.parse(uploaded_file, "fasta")
            )

            st.write(f"Total sequences: {len(sequences)}")

            if sequences:

                first_seq = str(sequences[0].seq)

                st.write("### First Sequence Preview")

                st.code(first_seq[:1000])

                file_content = first_seq[:5000]

        # -----------------------------------
        # TXT / VCF FILES
        # -----------------------------------

        else:

            content = uploaded_file.read().decode(
                "utf-8",
                errors="ignore"
            )

            st.write("### File Preview")

            st.code(content[:1500])

            file_content = content[:5000]

    except Exception as e:

        st.error(f"Error reading file: {e}")

# -----------------------------------
# LITERATURE SEARCH
# -----------------------------------

if uploaded_file:

    st.divider()

    st.subheader("📚 Literature Search")

    database = st.selectbox(
        "Database",
        [
            "PubMed",
            "PubMed Central (PMC)",
            "Bookshelf",
            "GeneReviews",
            "MeSH",
            "MedGen",
            "Journals"
        ]
    )

    literature_query = st.text_input(
        "Search",
        placeholder="BRCA1 breast cancer mutation"
    )

    max_results = st.slider(
        "Maximum Results",
        min_value=5,
        max_value=100,
        value=20
    )

    if st.button("Search Literature"):

    if literature_query:

        with st.spinner(f"Searching {database}..."):

            if database == "PubMed":
                papers = search_pubmed(
                    literature_query,
                    max_results
                )

            elif database == "PubMed Central (PMC)":
                papers = search_pmc(
                    literature_query,
                    max_results
                )

            elif database == "MeSH":
                papers = search_mesh(
                    literature_query,
                    max_results
                )

            elif database == "MedGen":
                papers = search_medgen(
                    literature_query,
                    max_results
                )

            else:
                papers = []

        st.success(f"Found {len(papers)} results")

        for paper in papers:

            st.markdown(
                f"### {paper['Title']}"
            )

            st.write(
                f"Journal: {paper.get('Journal', 'N/A')}"
            )

            with st.expander("Abstract"):
                st.write(
                    paper.get(
                        "Abstract",
                        "No abstract available."
                    )
                )
# -----------------------------------
# CHAT SECTION
# -----------------------------------

st.divider()

st.write("## Ask GenomeGPT")

example_questions = [
    "What mutations are present?",
    "Summarize this genome dataset",
    "Are there disease-associated variants?",
    "Explain this genomic data simply",
    "Which genes appear most important?",
    "Identify clinically relevant SNPs"
]

selected_question = st.selectbox(
    "Example Questions",
    [""] + example_questions
)

user_question = st.chat_input(
    "Ask a question about your uploaded genomic dataset..."
)

# -----------------------------------
# USE EXAMPLE QUESTION
# -----------------------------------

if not user_question and selected_question:
    user_question = selected_question

# -----------------------------------
# AI RESPONSE
# -----------------------------------

if user_question:

    st.chat_message("user").write(user_question)

    # -----------------------------------
    # DEMO MODE
    # -----------------------------------

    if not st.session_state.api_key_active:

        demo_response = f"""
🧬 GenomeGPT Demo Analysis

Analysis completed successfully.

Potential genes identified:
• APOE
• FCGR2A
• BRCA1

Possible findings:
• Immune-response related variants detected
• Lipid metabolism markers observed
• SNP-style genomic variations identified

Question analyzed:
"{user_question}"

⚠️ This response is generated in demo mode and does not represent medical advice.
        """

        st.chat_message("assistant").write(
            demo_response
        )

    # -----------------------------------
    # REAL AI MODE
    # -----------------------------------

    else:

        # REQUIRE FILE
        if not uploaded_file:

            st.warning(
                "Please upload a genomic dataset first."
            )

        else:

            prompt = f"""
You are GenomeGPT, an expert AI genomic research assistant.

Analyze this genomic dataset:

{file_content}

User Question:
{user_question}

Instructions:
- Be beginner friendly
- Explain genomic concepts clearly
- Mention possible genes and variants
- Avoid medical diagnosis
- Use bullet points when helpful
- Keep formatting clean
            """

            try:

                with st.spinner(
                    "🔬 Analyzing genomic dataset..."
                ):

                    response = client.chat.completions.create(
                        model="gpt-4.1-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are an expert genomics AI assistant."
                                )
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.3
                    )

                    ai_response = (
                        response.choices[0]
                        .message.content
                    )

                    st.chat_message("assistant").write(
                        ai_response
                    )

            except Exception as e:

                st.error(
                    f"OpenAI API Error: {e}"
                )

# -----------------------------------
# PUBMED SEARCH
# -----------------------------------

st.divider()

st.subheader("📚 Literature Search")

literature_query = st.text_input(
    "Search",
    placeholder="BRCA1 breast cancer mutation"
)

if st.button("Search Literature"):

    with st.spinner("Searching PubMed..."):

        papers = literature_search(
            literature_query,
            max_results=10
        )

    if papers:

        for paper in papers:

            st.markdown(
                f"### {paper['Title']}"
            )

            st.write(
                f"**Journal:** {paper['Journal']}"
            )

            st.write(
                f"**Year:** {paper['Year']}"
            )

            st.write(
                f"**PMID:** {paper['PMID']}"
            )

            with st.expander("Abstract"):
                st.write(
                    paper["Abstract"]
                )

    else:

        st.warning(
            "No papers found."
        )

# -----------------------------------
# FOOTER
# -----------------------------------

st.divider()

st.caption(
    "GenomeGPT • Educational Genomic AI Research Assistant"
)
