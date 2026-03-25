import streamlit as st
import os
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
from pydub import AudioSegment
import tempfile
import re
from datetime import datetime

AudioSegment.converter = "ffmpeg"

from utils.data_loader import (
    load_random_character,
    load_random_word,
    load_random_sentence,
    load_random_training_image
)
from utils.ocr import extract_text
from utils.text_compare import compare_texts
from utils.scoring import (
    calculate_stage_score,
    calculate_final_score,
    classify_risk,
    generate_interpretation
)
from utils.logger import save_record
from utils.pdf_generator import generate_pdf_report


st.set_page_config(page_title="Dyslexia Screening", page_icon="🧠", layout="wide")

# STYLING
st.markdown("""
<style>

/* ---------- Global Background ---------- */
.stApp {
    background: linear-gradient(135deg, #f4f7fb 0%, #e9f0f8 100%);
    font-family: 'Segoe UI', sans-serif;
}

/* ---------- Card Container ---------- */
.card {
    background: white;
    padding: 30px;
    border-radius: 18px;
    box-shadow: 0px 8px 25px rgba(0,0,0,0.08);
    margin-bottom: 25px;
}

/* ---------- Headings ---------- */
h1, h2, h3 {
    color: #1f3c88;
}

/* ---------- Buttons ---------- */
div.stButton > button {
    background-color: #1f77b4;
    color: white;
    font-weight: 600;
    border-radius: 10px;
    padding: 10px 18px;
    border: none;
    transition: all 0.3s ease-in-out;
}

div.stButton > button:hover {
    background-color: #125a8c;
    transform: scale(1.03);
}

/* ---------- Progress Bar ---------- */
.stProgress > div > div > div > div {
    background-color: #1f77b4;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background-color: #0e1a2b;
    color: white;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* ---------- Instruction Panel ---------- */
.instruction-box {
    background-color: #f1f6ff;
    padding: 15px;
    border-left: 5px solid #1f77b4;
    border-radius: 10px;
    margin-bottom: 20px;
    font-size: 15px;
}

/* ---------- Text Input Fields ---------- */
div[data-baseweb="input"] > div {
    border: 1.5px solid #cfd8e3 !important;
    border-radius: 8px !important;
    background-color: #ffffff !important;
}

/* Focus state */
div[data-baseweb="input"] > div:focus-within {
    border: 2px solid #1f3c88 !important;
    box-shadow: 0 0 0 1px #1f3c88 !important;
}

/* ---------- Text Area ---------- */
div[data-baseweb="textarea"] > div {
    border: 1.5px solid #cfd8e3 !important;
    border-radius: 8px !important;
    background-color: #ffffff !important;
}

div[data-baseweb="textarea"] > div:focus-within {
    border: 2px solid #1f3c88 !important;
    box-shadow: 0 0 0 1px #1f3c88 !important;
}

/* ---------- File Uploader ---------- */
section[data-testid="stFileUploader"] > div {
    border: 1.5px solid #cfd8e3 !important;
    border-radius: 8px !important;
    padding: 10px !important;
}

</style>
""", unsafe_allow_html=True)

TOTAL_STAGES = 4


# SESSION INITIALIZATION
defaults = {
    "page": "landing",
    "stage": 0,
    "stage_scores": {},
    "patient_data": {},
    "test_mode": None,
    "audio_input": "",
    "audio_confidence": 0.0,
    "test_data": {},
    "report_saved": False,
    "generated_pdf": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


PHONETIC_MAP = {
    "a": "a", "ay": "a", "alpha": "a",
    "b": "b", "bee": "b", "bravo": "b",
    "c": "c", "see": "c", "sea": "c", "charlie": "c",
    "d": "d", "dee": "d", "delta": "d",
    "e": "e", "ee": "e", "echo": "e",
    "f": "f", "ef": "f", "foxtrot": "f",
    "g": "g", "gee": "g", "golf": "g",
    "h": "h", "aitch": "h", "hotel": "h",
    "i": "i", "eye": "i", "india": "i",
    "j": "j", "jay": "j", "juliet": "j",
    "k": "k", "kay": "k", "kilo": "k",
    "l": "l", "el": "l", "lima": "l",
    "m": "m", "em": "m", "mike": "m", "am": "m",
    "n": "n", "en": "n", "november": "n",
    "o": "o", "oh": "o", "oscar": "o",
    "p": "p", "pee": "p", "papa": "p",
    "q": "q", "cue": "q", "quebec": "q",
    "r": "r", "are": "r", "romeo": "r",
    "s": "s", "ess": "s", "sierra": "s",
    "t": "t", "tee": "t", "tango": "t",
    "u": "u", "you": "u", "uniform": "u",
    "v": "v", "vee": "v", "victor": "v",
    "w": "w", "double": "w", "whiskey": "w",
    "x": "x", "ex": "x", "xray": "x",
    "y": "y", "why": "y", "yankee": "y",
    "z": "z", "zee": "z", "zed": "z", "zulu": "z"
}


def extract_letter_from_speech(transcript):

    if not transcript:
        return ""

    transcript = transcript.lower().strip()

    # Remove punctuation
    transcript = re.sub(r"[^\w\s]", "", transcript)

    words = transcript.split()

    # Step 1: If any single alphabet character exists
    for word in words:
        if len(word) == 1 and word.isalpha():
            return word

    # Step 2: Check phonetic map
    for word in words:
        if word in PHONETIC_MAP:
            return PHONETIC_MAP[word]

    return ""


def clean_audio_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s']", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def speech_to_text_from_browser(audio):

    recognizer = sr.Recognizer()

    try:
        if not audio or "bytes" not in audio:
            return "", 0.0

        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_webm:
            temp_webm.write(audio["bytes"])
            webm_path = temp_webm.name

        wav_path = webm_path.replace(".webm", ".wav")

        sound = AudioSegment.from_file(webm_path)
        sound = sound.set_channels(1)
        sound = sound.set_frame_rate(16000)
        sound.export(wav_path, format="wav")

        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)

        result = recognizer.recognize_google(audio_data, show_all=True)

        if not result or "alternative" not in result:
            return "", 0.0

        transcript = result["alternative"][0]["transcript"]
        confidence = result["alternative"][0].get("confidence", 0.0)

        os.remove(webm_path)
        os.remove(wav_path)

        return transcript, round(confidence * 100, 2)

    except:
        return "", 0.0


# RESET FUNCTIONS
def reset_test():
    st.session_state.stage = 0
    st.session_state.stage_scores = {}
    st.session_state.test_data = {}
    st.session_state.audio_input = ""
    st.session_state.audio_confidence = 0.0
    st.session_state.report_saved = False
    st.session_state.generated_pdf = None
    st.session_state.test_mode = None

    for key in ["current_character", "current_word",
                "current_sentence", "current_image"]:
        if key in st.session_state:
            del st.session_state[key]

    st.session_state.page = "test_selection"


def reset_all():
    for key in list(st.session_state.keys()):
        del st.session_state[key]    


# SIDEBAR
with st.sidebar:

    st.markdown("## Dyslexia Screening Portal")
    st.markdown("---")

    if st.session_state.page == "landing":
        st.write("### Navigation")
        if st.button("Proceed to Patient Registration"):
            st.session_state.page = "patient_info"
            st.rerun()

    else:
        st.write("### Navigation")

        if st.button("Home"):
            st.session_state.page = "landing"
            st.rerun()

        #if st.button("New Patient"):
        #    reset_all()
        #    st.rerun()

    st.markdown("---")

    if st.session_state.page == "test":
        st.write(f"Stage: {st.session_state.stage}/{TOTAL_STAGES}")
        st.write(f"Mode: {st.session_state.test_mode}")


# LANDING PAGE
if st.session_state.page == "landing":

    st.markdown("## Dyslexia Screening System")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2.5, 1])

    with col2:        

        st.markdown("### About Dyslexia")

        st.markdown("""
        Dyslexia is a neurodevelopmental learning difference that affects 
        reading accuracy, spelling, and phonological processing skills. 
        It is not related to intelligence and can occur in individuals 
        across all backgrounds.
        """)

        st.markdown("#### Common Indicators")
        st.markdown("""
        - Difficulty recognizing letters and sounds  
        - Slow or inaccurate word reading  
        - Inconsistent spelling patterns  
        - Challenges decoding unfamiliar words  
        """)

        st.markdown("#### About This Screening Tool")
        st.markdown("""
        This clinical screening tool evaluates foundational literacy skills through:
        - Character recognition  
        - Word reading  
        - Sentence processing  
        - Visual text interpretation  

        The results provide a preliminary risk assessment and 
        do not replace a formal diagnostic evaluation.
        """)

        st.markdown("<br>", unsafe_allow_html=True)
        st.write('---')


# PATIENT INFO
elif st.session_state.page == "patient_info":
    st.title("Patient Information")

    patient_id = st.text_input("Patient ID", max_chars=5)
    
    patient_name = st.text_input("Patient Name", max_chars=20)

    if st.button("Submit"):        
        if not patient_id.isdigit():
            st.error("Patient ID must contain only numbers")
        elif len(patient_id) > 5:
            st.error("Patient ID must be at most 5 digits")
        elif not re.fullmatch(r"[A-Za-z ]+", patient_name):
            st.error("Patient Name must contain only letters")
        elif len(patient_name) > 25:
            st.error("Patient Name must be at most 25 characters")
        else:            
            st.session_state.patient_data = {
                "id": patient_id,
                "name": patient_name
            }
            st.session_state.page = "test_selection"
            st.rerun()


# MODE SELECTION
elif st.session_state.page == "test_selection":
    st.title("Select Test Mode")
    st.markdown("""
        <div class="instruction-box">
        <b>Instructions:</b><br>
        • Carefully observe the letter,word or sentence shown.<br>
        • Respond clearly (type or speak).<br>
        • Accuracy is more important than speed.
        </div>
        """, unsafe_allow_html=True)
        
    st.write('----')
    
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Take Test in Text"):
            st.session_state.test_mode = "Text"
            st.session_state.stage = 1
            st.session_state.page = "test"
            st.rerun()

    with col2:
        if st.button("Take Test in Audio"):
            st.session_state.test_mode = "audio"
            st.session_state.stage = 1
            st.session_state.page = "test"
            st.rerun()


# TEST FLOW
elif st.session_state.page == "test":

    stage = st.session_state.stage
    mode = st.session_state.test_mode

    progress_value = stage / TOTAL_STAGES
    st.progress(progress_value)
    st.markdown(f"**Progress:** {int(progress_value * 100)}% Complete")
    st.caption(f"Stage {stage} of {TOTAL_STAGES}")

    # CHARACTER
    if stage == 1:        

        
        st.header("🔤 Character Recognition Test")

        if "current_character" not in st.session_state:
            st.session_state.current_character = load_random_character()

        target = st.session_state.current_character

        # ---------------- TEXT MODE ----------------
        if mode == "Text":
            st.subheader(f"Type the letter: {target}")
            user_input = st.text_input("Enter character")

        # ---------------- AUDIO MODE ----------------
        else:
            st.subheader(f"Say Letter: {target.lower()}")

            audio = mic_recorder("🎤 Start", "⏹ Stop", key="mic_character")

            extracted_letter = ""

            if audio:
                transcript, confidence = speech_to_text_from_browser(audio)

                extracted_letter = extract_letter_from_speech(transcript)

                if not extracted_letter and transcript:
                    for char in transcript:
                        if char.isalpha():
                            extracted_letter = char.lower()
                            break

                st.session_state.audio_input = extracted_letter
                st.session_state.audio_confidence = confidence

            user_input = st.text_input(
                "Recognized Letter",
                value=st.session_state.get("audio_input", "")
            )

        # ---------------- SUBMIT ----------------
        if st.button("Submit"):

            # Save ONLY single letter
            st.session_state.test_data["character_target"] = target
            st.session_state.test_data["character_response"] = user_input

            if mode == "audio":
                clean_target = target.lower()
                clean_response = user_input.lower()
            else:
                clean_target = target
                clean_response = user_input

            word_diff, char_diff = compare_texts(clean_target, clean_response)

            st.session_state.stage_scores["character"] = calculate_stage_score(
                word_diff, char_diff
            )

            st.session_state.stage += 1
            st.session_state.audio_input = ""
            
            st.rerun()
            

    # WORD
    elif stage == 2:
        
        st.header("Word Test")

        if "current_word" not in st.session_state:
            st.session_state.current_word = load_random_word()

        target = st.session_state.current_word

        if mode == "Text":
            st.subheader(f"Type the word: {target}")
            user_input = st.text_input("Enter word")
        else:
            st.subheader(f"Say the word: {target.lower()}")
            audio = mic_recorder("🎤 Start", "⏹ Stop", key="mic_word")

            if audio:
                transcript, confidence = speech_to_text_from_browser(audio)
                st.session_state.audio_input = transcript
                st.session_state.audio_confidence = confidence

            user_input = st.text_input("Recognized Text",
                                       value=st.session_state.get("audio_input", ""))

        if st.button("Submit"):
            st.session_state.test_data["word_target"] = target
            st.session_state.test_data["word_response"] = user_input

            clean_target = clean_audio_text(target) if mode == "audio" else target
            clean_response = clean_audio_text(user_input) if mode == "audio" else user_input

            word_diff, char_diff = compare_texts(clean_target, clean_response)
            st.session_state.stage_scores["word"] = calculate_stage_score(word_diff, char_diff)
            st.session_state.stage += 1
            st.session_state.audio_input = ""
            st.rerun()

    # SENTENCE
    elif stage == 3:
        
        st.header("Sentence Test")

        if "current_sentence" not in st.session_state:
            st.session_state.current_sentence = load_random_sentence()

        target = st.session_state.current_sentence

        if mode == "Text":
            st.subheader(f"Type the sentence: {target}")
            user_input = st.text_area("Enter sentence")
        else:
            st.subheader(f"Type the sentence: {target.lower()}")
            audio = mic_recorder("🎤 Start", "⏹ Stop", key="mic_sentence")

            if audio:
                transcript, confidence = speech_to_text_from_browser(audio)
                st.session_state.audio_input = transcript
                st.session_state.audio_confidence = confidence

            user_input = st.text_area("Recognized Text",
                                      value=st.session_state.get("audio_input", ""))

        if st.button("Submit"):
            st.session_state.test_data["sentence_target"] = target
            st.session_state.test_data["sentence_response"] = user_input

            clean_target = clean_audio_text(target) if mode == "audio" else target
            clean_response = clean_audio_text(user_input) if mode == "audio" else user_input

            word_diff, char_diff = compare_texts(clean_target, clean_response)
            st.session_state.stage_scores["sentence"] = calculate_stage_score(word_diff, char_diff)
            st.session_state.stage += 1
            st.session_state.audio_input = ""
            st.rerun()

    # IMAGE
    elif stage == 4:
        
        st.header("Image Text Test")

        if "current_image" not in st.session_state:
            st.session_state.current_image = load_random_training_image()

        image_path = st.session_state.current_image
        st.image(image_path, width=250)

        target = extract_text(image_path)

        if mode == "audio":
            audio = mic_recorder("🎤 Start", "⏹ Stop", key="mic_image")

            if audio:
                transcript, confidence = speech_to_text_from_browser(audio)
                st.session_state.audio_input = transcript
                st.session_state.audio_confidence = confidence

            user_input = st.text_area("Recognized Text",
                                      value=st.session_state.get("audio_input", ""))

        else:
            uploaded = st.file_uploader("Upload handwritten version",
                                        type=["png", "jpg", "jpeg"])
            user_input = ""

            if uploaded:
                temp_path = os.path.join(tempfile.gettempdir(), "uploaded_handwritten.png")
                with open(temp_path, "wb") as f:
                    f.write(uploaded.read())
                user_input = extract_text(temp_path)
                st.text_area("Extracted Text", value=user_input)

        if st.button("Submit"):
            st.session_state.test_data["image_target"] = target
            st.session_state.test_data["image_response"] = user_input

            clean_target = clean_audio_text(target) if mode == "audio" else target
            clean_response = clean_audio_text(user_input) if mode == "audio" else user_input

            word_diff, char_diff = compare_texts(clean_target, clean_response)
            st.session_state.stage_scores["image"] = calculate_stage_score(word_diff, char_diff)

            st.session_state.page = "result"
            st.rerun()


# RESULT
elif st.session_state.page == "result":

    st.header("Assessment Result")

    final_score = calculate_final_score(st.session_state.stage_scores)
    verdict = classify_risk(final_score)
    interpretation = generate_interpretation(final_score)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    record = {
        "Timestamp": timestamp,
        "Patient ID": st.session_state.patient_data.get("id", ""),
        "Patient Name": st.session_state.patient_data.get("name", ""),
        "Test Mode": st.session_state.test_mode,
        "Character Given": st.session_state.test_data.get("character_target", ""),
        "Character Response": st.session_state.test_data.get("character_response", ""),
        "Character Score": st.session_state.stage_scores.get("character", 0),
        "Word Given": st.session_state.test_data.get("word_target", ""),
        "Word Response": st.session_state.test_data.get("word_response", ""),
        "Word Score": st.session_state.stage_scores.get("word", 0),
        "Sentence Given": st.session_state.test_data.get("sentence_target", ""),
        "Sentence Response": st.session_state.test_data.get("sentence_response", ""),
        "Sentence Score": st.session_state.stage_scores.get("sentence", 0),
        "Image Text Given": st.session_state.test_data.get("image_target", ""),
        "Image Response": st.session_state.test_data.get("image_response", ""),
        "Image Score": st.session_state.stage_scores.get("image", 0),
        "Final Score": final_score,
        "Risk Level": verdict
    }

    if not st.session_state.report_saved:
        save_record(record)
        pdf_path = generate_pdf_report(record)
        st.session_state.generated_pdf = pdf_path
        st.session_state.report_saved = True
    else:
        pdf_path = st.session_state.generated_pdf

    st.metric("Final Score (%)", final_score)
    st.warning(verdict)
    st.info(interpretation)

    # Filename
    patient_id = st.session_state.patient_data.get("id", "UnknownID")
    patient_name = st.session_state.patient_data.get("name", "UnknownName")
    test_mode = st.session_state.test_mode

    safe_name = f"{patient_id}_{patient_name}_{test_mode}".replace(" ", "_")

    file_name = f"{safe_name}.pdf"

    with open(pdf_path, "rb") as file:
        st.download_button(
            "Download PDF Report",
            data=file,
            file_name=file_name,
            mime="application/pdf"
        )

    col1, col2 = st.columns(2)
    with col1:
        st.button("🔁 Retake Test (Same Patient)", on_click=reset_test)
    with col2:
        st.button("🆕 Start Over", on_click=reset_all)