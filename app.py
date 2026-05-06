import streamlit as st
import pandas as pd
from Bio import SeqIO
from openai import OpenAI

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

if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = True

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

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

    user_api_key = st.text_input(
        "Enter your OpenAI API key",
        type="password",
        placeholder="sk-...",
        help="Your API key is never stored"
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

        st.write("### AI Controls")

        st.session_state.demo_mode = st.toggle(
            "Demo Mode",
            value=st.session_state.demo_mode
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button("Use Demo"):
                st.session_state.demo_mode = True

        with col2:

            if st.button("Use Real AI"):
                st.session_state.demo_mode = False

        st.write("---")

        if st.button("Logout Admin"):

            st.session_state.admin_authenticated = False
            st.rerun()

    else:

        st.caption("🌐 Public Research Demo")

# -----------------------------------
# OPENAI CLIENT
# -----------------------------------

client = None

if user_api_key:

    try:

        client = OpenAI(
            api_key=user_api_key
        )

    except Exception as e:

        st.error(f"Invalid API Key: {e}")

# -----------------------------------
# STATUS
# -----------------------------------

if st.session_state.demo_mode:

    st.info(
        "🧪 Demo Mode Active • AI responses are simulated."
    )

else:

    st.success(
        "🤖 Real AI Mode Active"
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
    "Ask about your genomic data..."
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

    if st.session_state.demo_mode:

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

        # REQUIRE API KEY
        if not user_api_key:

            st.warning(
                "Please enter your OpenAI API key in the sidebar."
            )

        # REQUIRE FILE
        elif not uploaded_file:

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
# FOOTER
# -----------------------------------

st.divider()

st.caption(
    "GenomeGPT • Educational Genomic AI Research Assistant"
)
