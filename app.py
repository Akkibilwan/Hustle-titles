# app.py

import streamlit as st
import openai
import re
import io

# --- Page Configuration ---
st.set_page_config(
    page_title="Viral Shorts Title Generator 🚀",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- App Styling ---
st.markdown("""
<style>
    .stApp {
        background-color: #1a1a1a;
        color: #e6e6e6;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #ff6a6a;
    }
    .stSelectbox div[data-baseweb="select"] {
        background-color: #333333;
    }
    .stTextArea textarea {
        background-color: #333333;
        color: #e6e6e6;
    }
    h1, h2, h3 {
        color: #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)


# --- Helper Functions ---

def parse_srt(file_content):
    """Parses an SRT file content and extracts only the dialogue."""
    try:
        # Decode bytes to string
        srt_text = file_content.decode('utf-8')
        # Regex to remove timestamps, sequence numbers, and formatting tags
        text_only = re.sub(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '', srt_text)
        text_only = re.sub(r'<[^>]+>', '', text_only)
        text_only = re.sub(r'^\s*$', '', text_only, flags=re.MULTILINE)
        return "\n".join(text_only.splitlines())
    except Exception as e:
        st.error(f"Error parsing SRT file: {e}")
        return None

def get_engineered_prompt(transcript_text):
    """
    Constructs a refined, aggressive prompt for shorter, catchier, and cliffhanger-style headlines.
    """
    return f"""
# [ROLE]
You are a cutting-edge Viral Content Strategist for YouTube Shorts, an expert in creating high-retention, scroll-stopping content for the Indian market as of August 2025. Your entire focus is on creating maximum curiosity in minimum time.

# [TASK]
Analyze the provided transcript to generate two sets of text. The top priority is creating an irresistible urge to watch the video.

# [INPUT]
TRANSCRIPT: \"\"\"
{transcript_text}
\"\"\"

# [GENERATION GUIDELINES]

## 1. On-Video Headlines (10 Options)
Your instructions for this section are VERY STRICT.
- **Goal:** Create an irresistible cliffhanger or a shocking statement. Make the viewer feel they *must* know the answer.
- **Length:** **STRICTLY 3-5 WORDS.** This is crucial.
- **Style:**
    - **MUST** include 1-2 powerful emojis (e.g., 🤫, 🤯, 🚨, 💰, 🚩).
    - **DO NOT** use full sentences. Use punchy phrases.
    - Frame it as a secret, a warning, or a shocking revelation.
- **Examples of the required style:** "Their Secret Pay Trick 🤫", "The 12-Hour Lie 🤯", "Never Sign This... 🚨"

## 2. YouTube Video Titles (10 Options)
- **Goal:** Maximize Click-Through Rate (CTR) with a punchy, benefit-driven title.
- **Length:** Keep under 70 characters.
- **Style:** Start with the most impactful phrase. Use strong keywords and power words. Combine the celebrity asset (if any) with the core conflict. Make it feel like an exposé.

# [OUTPUT FORMAT]
Present your final output in clean Markdown tables as specified below.

### **A. On-Video Headlines**
Create a table with three columns: `Headline (On-Video Text)`, `Viral Score (out of 10)`, and `Why It Works`.

### **B. YouTube Video Titles**
Create a second table with three columns: `YouTube Title`, `Viral Score (out of 10)`, and `Why It Works`.
"""

# --- Main App ---

st.title("🎬 Viral Shorts Title & Headline Generator")
st.markdown("Generate killer titles and headlines for your YouTube Shorts using AI. Just provide your video's transcript!")

# --- Sidebar for Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Check for API Key
    try:
        openai.api_key = st.secrets["OPENAI_API_KEY"]
    except (KeyError, FileNotFoundError):
        st.error("`secrets.toml` not found or `OPENAI_API_KEY` is missing.")
        st.info("Please create a `.streamlit/secrets.toml` file and add your OpenAI API key.")
        st.stop()

    # Fetch and select model
    try:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        models = [model.id for model in client.models.list()]
        # Filter for GPT models for relevance
        gpt_models = sorted([m for m in models if 'gpt' in m], reverse=True)
        
        # Set default model
        default_model_name = "gpt-4o-mini"
        default_index = gpt_models.index(default_model_name) if default_model_name in gpt_models else 0
        
        selected_model = st.selectbox(
            "Choose your AI Model",
            gpt_models,
            index=default_index,
            help="Select the AI model to generate content. `gpt-4o-mini` is recommended for a balance of cost and quality."
        )
    except Exception as e:
        st.error(f"Could not fetch OpenAI models: {e}")
        st.warning("Using default model. Please check your API key and OpenAI status.")
        selected_model = "gpt-4o-mini"


    st.markdown("---")
    st.markdown("Built by Gemini")
    st.markdown("Inspired by the needs of modern content creators.")


# --- Main Content Area ---

# Input Section
st.header("1. Provide Your Video Transcript")

input_method = st.radio(
    "Choose your input method:",
    ("Paste Text", "Upload .txt File", "Upload .srt File"),
    horizontal=True
)

transcript_input = ""

if input_method == "Paste Text":
    transcript_input = st.text_area("Paste your full transcript here:", height=200, placeholder="When I was doing TV, we used to get 4 days for a 12 hour shift...")
elif input_method == "Upload .txt File":
    uploaded_txt = st.file_uploader("Upload a .txt file", type=['txt'])
    if uploaded_txt:
        transcript_input = uploaded_txt.read().decode('utf-8')
        st.success("TXT file uploaded and processed!")
elif input_method == "Upload .srt File":
    uploaded_srt = st.file_uploader("Upload a .srt file", type=['srt'])
    if uploaded_srt:
        transcript_input = parse_srt(uploaded_srt.getvalue())
        if transcript_input:
            st.success("SRT file uploaded and dialogue extracted!")


# Generation Section
st.header("2. Generate Your Content")

if st.button("🚀 Generate Titles & Headlines"):
    if not transcript_input or not transcript_input.strip():
        st.warning("Please provide a transcript before generating.")
    else:
        with st.spinner("🧠 AI is thinking... Crafting the perfect hooks..."):
            try:
                # The function is now called correctly with the user's input
                prompt = get_engineered_prompt(transcript_input)
                
                client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                
                response = client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {"role": "system", "content": "You are a world-class Viral Content Strategist for YouTube."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                result = response.choices[0].message.content
                
                st.header("✅ Here are your generated results:")
                st.markdown(result)

            except openai.APIError as e:
                st.error(f"An OpenAI API error occurred: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
