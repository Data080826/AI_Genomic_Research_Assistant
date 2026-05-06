import streamlit as st
import pandas as pd
from Bio import SeqIO
from openai import OpenAI
import io

# -------------------------------
# PAGE CONFIG
# -------------------------------

st.set_page_config(
    page_title="GenomeGPT",
    layout="wide"
)

st.title("🧬 GenomeGPT")
st.subheader("AI-Powered Genomic Research Assistant")

st.info(
    "Demo Version • Uses sample AI responses to avoid excessive API usage."
)

# -------------------------------
# SIDEBAR
# -------------------------------

st.sidebar.title("Settings")

demo_mode = st.sidebar.toggle(
    "Demo Mode",
    value=True
)

# Optional real AI mode
if not demo_mode:

    api_key = st.secrets["OPENAI_API_KEY"]

    client = OpenAI(api_key=api_key)

# -------------------------------
# FILE UPLOAD
# -------------------------------

uploaded_file = st.file_uploader(
    "Upload a genome dataset",
    type=["csv", "fasta", "fa", "txt", "vcf"]
)

# -------------------------------
# FILE PREVIEW
# -------------------------------

if uploaded_file:

    st.success("File uploaded successfully")

    # CSV
    if uploaded_file.name.endswith(".csv"):

        df = pd.read_csv(uploaded_file)

        st.write("### Dataset Preview")
        st.dataframe(df.head())

        st.write("### Dataset Shape")
        st.write(df.shape)

        st.write("### Columns")
        st.write(df.columns.tolist())

    # FASTA
    elif uploaded_file.name.endswith((".fasta", ".fa")):

        sequences = list(
            SeqIO.parse(uploaded_file, "fasta")
        )

        st.write(f"Total sequences: {len(sequences)}")

        if sequences:

            st.write("### First Sequence")

            st.code(
                str(sequences[0].seq[:500])
            )

    # TXT / VCF
    else:

        content = uploaded_file.read().decode("utf-8")

        st.write("### File Preview")

        st.code(content[:1000])

# -------------------------------
# CHAT SECTION
# -------------------------------

st.divider()

st.write("### Ask GenomeGPT")

example_questions = [
    "What mutations are present?",
    "Summarize this genome dataset",
    "Are there disease-associated variants?",
    "Explain this genomic data simply"
]

selected_question = st.selectbox(
    "Try an example question",
    [""] + example_questions
)

user_question = st.chat_input(
    "Ask questions about your genome data..."
)

# Use selected example if chat empty
if not user_question and selected_question:
    user_question = selected_question

# -------------------------------
# AI RESPONSE
# -------------------------------

if user_question:

    st.chat_message("user").write(user_question)

    # -------------------------------
    # DEMO MODE RESPONSES
    # -------------------------------

    if demo_mode:

        demo_response = """
🧬 Demo Analysis Complete

GenomeGPT identified several example genomic variants
commonly associated with immune response and lipid metabolism.

Possible genes detected:
• APOE
• FCGR2A

Example insights:
• APOE variants may influence cholesterol processing
• FCGR2A is involved in immune system signaling

This is a simulated AI-generated response for demonstration purposes.
        """

        st.chat_message("assistant").write(
            demo_response
        )

    # -------------------------------
    # REAL AI MODE
    # -------------------------------

    else:

        if uploaded_file is None:

            st.warning(
                "Please upload a genome dataset first."
            )

        else:

            file_content = ""

            # CSV
            if uploaded_file.name.endswith(".csv"):

                uploaded_file.seek(0)

                df = pd.read_csv(uploaded_file)

                # limit size
                file_content = df.head(20).to_string()

            # OTHER FILES
            else:

                uploaded_file.seek(0)

                file_content = uploaded_file.read().decode(
                    "utf-8"
                )[:5000]

            prompt = f"""
You are a genomics AI assistant.

Here is the uploaded genome dataset:

{file_content}

User question:
{user_question}

Provide a beginner-friendly explanation.
            """

            with st.spinner("Analyzing genomic data..."):

                response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert genomic "
                                "research assistant."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                ai_response = (
                    response.choices[0]
                    .message.content
                )

                st.chat_message("assistant").write(
                    ai_response
                )

# -------------------------------
# FOOTER
# -------------------------------

st.divider()

st.caption(
    "GenomeGPT • Educational demo project for genomic AI analysis"
)
