import streamlit as st
import google.generativeai as genai
import google.api_core.exceptions
from gtts import gTTS
import requests
from PIL import Image
from io import BytesIO
import base64
import time
import os
import random

# --- Page Configuration ---
st.set_page_config(
    page_title="The Honest Woodcutter - Interactive Story",
    page_icon="🌳",
    layout="wide"
)

# --- Cocomelon-themed CSS with Invisible Boxes ---
st.markdown(
    """
    <style>
    /* Import playful fonts */
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;700&family=Balsamiq+Sans:wght@400;700&display=swap');

    /* Full-page background image (The Scene Illustration itself!) */
    .stApp {
        background-color: #f0f8ff; /* Fallback color */
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        transition: background-image 0.5s ease-in-out; /* Smooth transition for background image changes */
    }

    /* General font for main content */
    body, .stMarkdown, p, div {
        font-family: 'Balsamiq Sans', cursive;
        font-size: 1.15rem;
        line-height: 1.6;
        color: #333; /* Dark grey for readability */
    }

    /* Main title styling */
    h1 {
        font-family: 'Fredoka', sans-serif !important;
        color: #FF69B4 !important; /* Hot Pink */
        text-shadow: 3px 3px #87CEFA, 5px 5px #4682B4 !important; /* Sky Blue & Steel Blue for pop */
        font-size: 3.8rem !important;
        text-align: center;
        margin-top: 0;
        padding-top: 20px;
    }

    /* Subtitle and other headings */
    h2, h3 {
        font-family: 'Fredoka', sans-serif !important;
        color: #FFD700 !important; /* Gold for emphasis */
        text-shadow: 2px 2px #FFA07A !important; /* Light Salmon */
        font-size: 2.2rem;
    }

    /* Hide the default Streamlit main content div background to let our custom box shine */
    .main > div {
        background: none !important;
    }
    /* Hide all column backgrounds and box shadows */
    .stColumn > div {
        background: none !important;
        box-shadow: none !important;
    }
    /* Hide backgrounds and borders for alerts and info messages */
    .stAlert, .stSpinner, .stProgress, .stAudio, .stDownloadButton, .stInfo, .stSuccess, .stWarning {
        background: rgba(255, 255, 255, 0.1) !important; /* Semi-transparent white for readability */
        border-radius: 15px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
        padding: 15px !important;
        margin: 10px 0 !important;
        border: none !important;
    }

    .stInfo { border-left: 8px solid #87CEFA !important; /* Sky Blue */ }
    .stSuccess { border-left: 8px solid #98FB98 !important; /* Pale Green */ }
    .stWarning { border-left: 8px solid #FFD700 !important; /* Gold */ }

    /* Sidebar styling with playful colors */
    .css-1d391kg, .stSidebar {
        background-color: rgba(255, 255, 255, 0.05); /* Blush Pink with transparency */
        border-right: 5px solid #FF69B4; /* Hot Pink border */
        border-radius: 0 25px 25px 0;
        box-shadow: 8px 0 20px rgba(0,0,0,0.15);
        padding: 20px;
    }
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
        color: #FF69B4 !important; /* Hot Pink */
        text-shadow: 1px 1px #fff !important;
    }
    .css-1d391kg label, .css-1d391kg .stRadio {
        font-family: 'Balsamiq Sans', cursive;
        color: #4682B4; /* Steel Blue */
    }

    /* Button styling - playful and pill-shaped */
    .stButton>button {
        background: linear-gradient(45deg, #FF69B4, #FFD700) !important; /* Pink to Gold gradient */
        color: white !important;
        border-radius: 30px !important;
        border: 4px solid #fff !important;
        font-size: 1.3rem !important;
        padding: 15px 30px !important;
        font-family: 'Fredoka', sans-serif !important;
        box-shadow: 0 8px 20px rgba(255,105,180,0.4);
        transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 10px; /* Space out buttons */
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #FFD700, #FF69B4) !important; /* Reverse gradient on hover */
        transform: translateY(-5px) scale(1.08) rotate(2deg);
        box-shadow: 0 12px 30px rgba(255,105,180,0.6);
    }

    /* Audio player styling */
    audio {
        border-radius: 25px;
        filter: hue-rotate(30deg);
        margin-top: 20px;
        width: 80%;
    }

    /* Download button special styling */
    .stDownloadButton > button {
        background: linear-gradient(45deg, #87CEFA, #4682B4) !important; /* Sky Blue to Steel Blue */
        border-radius: 25px !important;
        box-shadow: 0 5px 15px rgba(135,206,250,0.4) !important;
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(45deg, #4682B4, #87CEFA) !important;
    }

    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #FFC0CB, #FFD700, #87CEFA, #FFC0CB) !important; /* Pink, Gold, Blue gradient */
        background-size: 300% 300% !important;
        animation: gradient-flow 2s ease infinite !important;
        border-radius: 10px !important;
        height: 18px !important;
    }
    @keyframes gradient-flow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Footer styling */
    .footer {
        text-align: center;
        margin-top: 30px;
        padding: 15px;
        background-color: rgba(255, 255, 255, 0.7);
        border-top: 3px solid #FFC0CB;
        border-radius: 15px 15px 0 0;
        font-family: 'Balsamiq Sans', cursive;
        color: #4682B4;
    }

    /* Narration and choices should be in the center, floating over the background */
    .st-emotion-cache-1pxx7z6 { /* Targets the main content block */
        max-width: 900px;
        margin: auto;
    }

    /* Special styling for the main narration text to float over image better */
    .story-narration-box {
        background-color: rgba(255, 255, 255, 0.75); /* More transparent for overlay */
        border-radius: 20px;
        padding: 25px;
        margin-top: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        font-family: 'Balsamiq Sans', cursive;
        font-size: 1.25rem;
        color: #333;
        max-width: 80%;
        text-align: center;
        margin-left: auto;
        margin-right: auto;
    }

    /* Custom class for the image that will be the main background */
    .main-background-image {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        z-index: -1; /* Place behind other content */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- API Configuration ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")


# --- Helper Functions ---
def generate_story_narration(scene_text):
    """
    Uses the Gemini API to retell the current scene with kid-friendly narration.
    """
    try:
        response = model.generate_content(
            f"""
            You are a kind and engaging storyteller for kids.
            Retell the following story scene in 3-5 sentences with emotions,
            simple words, and a magical feel.
            Scene: {scene_text}
            """
        )
        return response.text.strip()
    except google.api_core.exceptions.NotFound:
        st.error("Error: The requested model was not found. Please check the model name or your API key region.")
        return "The magical storyteller is unavailable. Please try again later."
    except Exception as e:
        st.error(f"Error calling the Gemini API: {e}")
        return "The magical storyteller is taking a nap. Please try again!"


def get_local_image_for_scene(scene_key):
    """
    Randomly selects a local image from a directory corresponding to the scene.
    """
    image_dir = os.path.join("images", scene_key)
    if not os.path.exists(image_dir):
        st.warning(f"Image directory '{image_dir}' not found.")
        return None

    images = [f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    if not images:
        st.warning(f"No images found in '{image_dir}'.")
        return None

    image_path = os.path.join(image_dir, random.choice(images))
    return Image.open(image_path)


def generate_image(scene_text, scene_key):
    """
    Generates an image for the story scene using Hugging Face's API with a local image fallback.
    """
    try:
        prompt = f"children's book illustration, watercolor style, {scene_text[:200]}, magical, colorful, friendly"
        API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"

        headers = {}
        if "HUGGINGFACE_TOKEN" in st.secrets:
            headers = {"Authorization": f"Bearer {st.secrets['HUGGINGFACE_TOKEN']}"}

        payload = {"inputs": prompt}
        response = requests.post(API_URL, headers=headers, json=payload, timeout=15)

        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        else:
            st.warning("Image generation API is busy. Using local image.")
            return get_local_image_for_scene(scene_key)

    except Exception as e:
        st.warning(f"Could not generate image: {e}. Using local image.")
        return get_local_image_for_scene(scene_key)


def create_placeholder_image(text):
    """
    Creates a simple placeholder image when API fails.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (400, 300), color=(135, 206, 235))
        draw = ImageDraw.Draw(img)
        draw.ellipse([20, 20, 80, 80], fill=(255, 255, 0))
        draw.rectangle([0, 200, 400, 300], fill=(34, 139, 34))
        text_lines = text[:100].split()
        y_position = 100
        for i in range(0, len(text_lines), 5):
            line = ' '.join(text_lines[i:i + 5])
            draw.text((20, y_position), line, fill=(0, 0, 0))
            y_position += 20
        return img
    except:
        return None


def generate_voice(text, voice_type="female"):
    """
    Generates voice narration for the story text using gTTS.
    """
    try:
        voice_settings = {
            "male": {"lang": "en", "tld": "com.au", "slow": False},
            "female": {"lang": "en", "tld": "co.uk", "slow": False},
            "kid": {"lang": "en", "tld": "com", "slow": True}
        }
        settings = voice_settings.get(voice_type, voice_settings["female"])
        tts = gTTS(
            text=text,
            lang=settings["lang"],
            tld=settings["tld"],
            slow=settings["slow"]
        )
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.getvalue()
    except Exception as e:
        st.warning(f"Could not generate voice: {e}")
        return None


# --- Story Data Structure ---
story = {
    "start": {
        "text": "Once, a poor but honest woodcutter was working near a river. His axe, his only tool, slipped and fell into the deep water. He sat on the bank and began to cry. Suddenly, a goddess rose from the water holding a beautiful golden axe. 'Is this yours?' she asked.",
        "choices": {
            "Yes, that's my axe!": "lie_ending",
            "No, that is not mine. My axe was made of iron.": "honest_ending"
        }
    },
    "lie_ending": {
        "text": "The woodcutter lied and said the golden axe was his. The goddess, knowing the truth, disappeared, taking the golden axe with her. The woodcutter was left with nothing.",
        "moral_outcome": "Dishonesty leads to loss.",
        "choices": {}
    },
    "honest_ending": {
        "text": "The woodcutter told the truth. The goddess smiled, pleased with his honesty. 'Because of your honesty, you may have both your iron axe and this golden axe!' she said. A few moments later, she returned with a silver axe. 'Is this your axe?'",
        "choices": {
            "Yes! Thank you!": "greedy_ending",
            "No, that is not mine either.": "truly_honest_ending"
        }
    },
    "greedy_ending": {
        "text": "The woodcutter, surprised by the new axe, lied again. The goddess frowned and disappeared. The woodcutter was left with nothing.",
        "moral_outcome": "Greed takes away even what you have.",
        "choices": {}
    },
    "truly_honest_ending": {
        "text": "The woodcutter, true to his word, declined the silver axe as well. The goddess, impressed by his unwavering honesty, rewarded him with all three axes—the iron, the silver, and the gold. He became a very rich man and lived happily ever after.",
        "moral_outcome": "Honesty always brings great rewards.",
        "choices": {}
    }
}

# --- Main Streamlit App ---
st.title("🌳 The Honest Woodcutter - An Interactive Moral Story")
st.markdown("*An enchanting story with AI-generated narration, illustrations, and voice!*")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Story Settings")
    voice_type = st.radio(
        "Select voice type:",
        options=["female", "male", "kid"],
        index=0,
        help="Choose how you want the story to be narrated"
    )
    if "voice_type" not in st.session_state:
        st.session_state.voice_type = "female"
    st.session_state.voice_type = voice_type
    st.markdown("---")
    st.subheader("📊 Your Journey")
    if "current_story_part" in st.session_state:
        progress_map = {
            "start": 0.2,
            "lie_ending": 1.0,
            "honest_ending": 0.6,
            "greedy_ending": 1.0,
            "truly_honest_ending": 1.0
        }
        progress = progress_map.get(st.session_state.current_story_part, 0)
        st.progress(progress)
    st.markdown("---")
    st.info(
        "**About this Story:**\n\n"
        "This interactive story teaches children about "
        "the importance of honesty through choices and consequences. "
        "Each decision leads to a different path!"
    )

if "current_story_part" not in st.session_state:
    st.session_state.current_story_part = "start"

current_data = story[st.session_state.current_story_part]

# --- Main Content Area (Story, Image, Choices) ---

# Generate and apply the image to the *main background* dynamically
with st.spinner("🎨 Crafting the perfect scene..."):
    scene_image_pil = generate_image(current_data["text"], st.session_state.current_story_part)
    if scene_image_pil:
        buffered = BytesIO()
        scene_image_pil.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{img_str}");
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.info("No scene image available.")

# Narration
with st.spinner("✨ The storyteller is preparing the scene..."):
    ai_narration = generate_story_narration(current_data["text"])
st.markdown(f'<div class="story-narration-box">{ai_narration}</div>', unsafe_allow_html=True)

# Audio
voice_type = st.session_state.get("voice_type", "female")
with st.spinner(f"🎙️ Generating {voice_type} voice..."):
    audio_data = generate_voice(ai_narration, voice_type)
    if audio_data:
        st.audio(audio_data, format='audio/mp3')
        st.download_button(
            label="📥 Download Audio",
            data=audio_data,
            file_name=f"story_narration_{st.session_state.current_story_part}.mp3",
            mime="audio/mp3"
        )

# Choices
st.markdown("---")  # Visual separator for choices
if not current_data["choices"]:
    st.balloons()
    st.success("### 🌟 Moral of the Story")
    st.info(f"**{current_data.get('moral_outcome', 'Every choice teaches us something!')}**")

    if st.button("🔄 Play Again", use_container_width=True):
        st.session_state.current_story_part = "start"
        st.rerun()
else:
    st.subheader("🤔 What would you do?")
    cols = st.columns(len(current_data["choices"]))
    for i, (choice_text, next_part) in enumerate(current_data["choices"].items()):
        with cols[i]:
            if st.button(choice_text, use_container_width=True):
                st.session_state.current_story_part = next_part
                st.rerun()

# --- Footer ---
st.markdown(
    "<p class='footer'>"
    "Made with ❤️ • Teaching kids the value of honesty"
    "</p>",
    unsafe_allow_html=True
)
