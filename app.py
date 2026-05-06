import streamlit as st
import pandas as pd
from Bio import SeqIO
from openai import OpenAI
import os

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

st.set_page_config(page_title="GenomeGPT", layout="wide")

st.title("🧬 GenomeGPT")
st.subheader("AI-Powered Genomic Research Assistant")

uploaded_file = st.file_uploader(
    "Upload a genome dataset",
    type=["csv", "fasta", "fa", "txt"]
)

# -------------------------------
# CSV HANDLING
# -------------------------------

if uploaded_file:

    st.success("File uploaded successfully")

    if uploaded_file.name.endswith(".csv"):

        df = pd.read_csv(uploaded_file)

        st.write("### Dataset Preview")
        st.dataframe(df.head())

        st.write("### Dataset Shape")
        st.write(df.shape)

        st.write("### Columns")
        st.write(df.columns.tolist())

    # -------------------------------
    # FASTA HANDLING
    # -------------------------------

    elif uploaded_file.name.endswith((".fasta", ".fa")):

        sequences = list(SeqIO.parse(uploaded_file, "fasta"))

        st.write(f"Total sequences: {len(sequences)}")

        if sequences:
            st.write("### First Sequence")
            st.code(str(sequences[0].seq[:500]))
# -------------------------------
# CHATBOT SECTION
# -------------------------------

st.divider()

user_question = st.chat_input(
    "Ask questions about your genome data..."
)

if user_question:

    st.chat_message("user").write(user_question)

    file_content = ""

    # READ CSV
    if uploaded_file.name.endswith(".csv"):

        uploaded_file.seek(0)

        file_content = pd.read_csv(
            uploaded_file
        ).to_string()

    # READ FASTA / TXT / VCF
    else:

        uploaded_file.seek(0)

        file_content = uploaded_file.read().decode("utf-8")

    prompt = f"""
    You are a genomics AI assistant.

    Here is the uploaded genome dataset:

    {file_content}

    User question:
    {user_question}

    Analyze the genomic data and provide
    a clear beginner-friendly explanation.
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert genomic data assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    ai_response = response.choices[0].message.content

    st.chat_message("assistant").write(ai_response)
