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
    """Constructs the detailed, engineered prompt for the AI model."""
    # This function now correctly takes the transcript text as an argument
    # and builds the prompt inside the function call.
    return f"""
# [ROLE]
You are a world-class Viral Content Strategist and YouTube expert. Your specialization is the Indian digital media market, and you are fully aware of trends, audience psychology, and effective content formats as of August 2025.

# [CONTEXT]
- **Audience Focus:** Your recommendations must resonate with the modern Indian YouTube audience.
- **Platform Nuances:** The primary goal is for YouTube Shorts, which prioritizes high-retention hooks in the first 1-3 seconds. Titles must be compelling enough to drive clicks from the Shorts feed and YouTube search.

# [TASK]
Your objective is to analyze the provided video transcript and generate two distinct sets of viral-optimized text:
1.  **On-Video Headlines:** 10 options of ultra-short text designed to be overlaid on the video to stop viewers from scrolling.
2.  **YouTube Video Titles:** 10 options of SEO-friendly and click-driven titles for the video upload itself.

You must also score each suggestion out of 10 and provide a clear justification for its potential success.

# [INPUT]
TRANSCRIPT: \"\"\"
{transcript_text}
\"\"\"

# [ANALYSIS FRAMEWORK]
Before generating, you must mentally perform this analysis of the transcript:
1.  **Identify the Core Conflict:** What is the central comparison or tension in the text?
2.  **Pinpoint the "Golden Nugget":** What is the single most surprising, memorable, or intriguing phrase or concept?
3.  **Determine the Emotional Angle:** What emotion should the title evoke? (e.g., Shock, Curiosity, Validation, Exclusivity).
4.  **Extract SEO Keywords:** Identify essential search terms.

# [OUTPUT FORMAT]
Present your final output in a clean, readable Markdown format. Follow this structure precisely:

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
