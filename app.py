import streamlit as st
import os
import time
import glob
import cv2
import numpy as np
import pytesseract
from PIL import Image
from gtts import gTTS
from deep_translator import GoogleTranslator  # ✅ reemplazo de googletrans

# CONFIGURACIÓN GENERAL
st.set_page_config(
    page_title="OCR y Traducción con Audio",
    page_icon="🎧",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 🎨 ESTILOS VISUALES COMPLETOS
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #e6e4ff 0%, #d9f4ff 100%);
        color: #1f244b;
        font-family: 'Poppins', sans-serif;
    }

    h1, h2, h3 {
        color: #1f244b;
        text-align: center;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    section[data-testid="stSidebar"] {
        background-color: #efeaff;
        border-right: 2px solid #c4b8ff;
        color: #1f244b;
    }

    section[data-testid="stSidebar"] * {
        color: #1f244b !important;
        font-size: 15px;
    }

    div.stButton > button {
        background: linear-gradient(90deg, #b9a6ff 0%, #a1e3ff 100%);
        color: #1f244b;
        font-weight: 600;
        border-radius: 10px;
        border: none;
        padding: 8px 24px;
        font-size: 15px;
        transition: all 0.3s ease;
        box-shadow: 0px 3px 10px rgba(0,0,0,0.15);
    }

    div.stButton > button:hover {
        background: linear-gradient(90deg, #a694ff 0%, #8fd8ff 100%);
        transform: scale(1.05);
    }

    textarea, input, select {
        background-color: #ffffff !important;
        color: #1f244b !important;
        border-radius: 10px !important;
        border: 1px solid #b9b9d9 !important;
    }

    img {
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }

    audio {
        border-radius: 10px;
        border: 2px solid #b7a6ff;
    }

    [data-testid="stHeader"] {
        background: linear-gradient(90deg, #b7a6ff 0%, #9be4ff 100%) !important;
        color: #1f244b !important;
        height: 3.2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    /* Forzar color de etiquetas de widgets en el contenido principal */
    [data-testid="stWidgetLabel"],
    [data-testid="stCheckbox"] > label,
    div[data-baseweb="checkbox"] label {
      color: #1f244b !important;
    }

    /* Label del file_uploader ("Cargar una imagen") */
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] p {
      color: #1f244b !important;
    }

    /* Texto genérico dentro de contenedores markdown */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span {
      color: #1f244b !important;
    }

    .stAlert p {
        color: #1f244b !important;
    }

    .stSuccess, .stInfo {
        color: #1f244b !important;
    }
    </style>
""", unsafe_allow_html=True)

# FUNCIONES AUXILIARES
def traducir_texto(text, src, dest):
    """Traduce texto usando deep-translator"""
    return GoogleTranslator(source=src, target=dest).translate(text)

def text_to_speech(input_language, output_language, text, tld):
    trans_text = traducir_texto(text, input_language, output_language)
    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
    my_file_name = text[0:20] if text.strip() else "audio"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, trans_text

def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if mp3_files:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)

remove_files(7)

# INTERFAZ PRINCIPAL
st.title("Reconocimiento Óptico de Caracteres (OCR)")
st.subheader("Convierte texto desde imágenes, tradúcelo y genera audio fácilmente.")

cam_ = st.checkbox("Usar cámara")

if cam_:
    img_file_buffer = st.camera_input("Toma una foto")
else:
    img_file_buffer = None

with st.sidebar:
    st.subheader("Procesamiento de Imagen")
    filtro = st.radio("Aplicar filtro a la imagen de cámara", ('Sí', 'No'))

# SUBIDA DE IMAGEN
bg_image = st.file_uploader("Cargar una imagen:", type=["png", "jpg", "jpeg"])
if bg_image is not None:
    uploaded_file = bg_image
    st.image(uploaded_file, caption='Imagen cargada', use_container_width=True)

    with open(uploaded_file.name, 'wb') as f:
        f.write(uploaded_file.read())

    img_cv = cv2.imread(uploaded_file.name)
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    st.write("Texto detectado en la imagen:")
    st.success(text)

# CAPTURA DESDE CÁMARA
if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    if filtro == 'Sí':
        cv2_img = cv2.bitwise_not(cv2_img)

    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    st.write("Texto detectado:")
    st.success(text)

# PANEL DE TRADUCCIÓN Y AUDIO
with st.sidebar:
    st.subheader("Parámetros de Traducción y Audio")

    try:
        os.mkdir("temp")
    except:
        pass

    in_lang = st.selectbox(
        "Lenguaje de entrada",
        ("Inglés", "Español", "Coreano", "Mandarín", "Japonés"),
    )
    lang_map = {
        "Inglés": "en",
        "Español": "es",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja"
    }
    input_language = lang_map.get(in_lang, "en")

    out_lang = st.selectbox(
        "Lenguaje de salida",
        ("Español", "Inglés", "Coreano", "Mandarín", "Japonés"),
    )
    output_language = lang_map.get(out_lang, "es")

    accent = st.selectbox(
        "Acento",
        ("Defecto", "Reino Unido", "Estados Unidos", "Australia", "Irlanda", "Sudáfrica", "España"),
    )
    tld_map = {
        "Defecto": "com",
        "Reino Unido": "co.uk",
        "Estados Unidos": "com",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sudáfrica": "co.za",
        "España": "es"
    }
    tld = tld_map.get(accent, "com")

    display_output_text = st.checkbox("Mostrar texto traducido")

    if st.button("Convertir a Audio"):
        if text.strip() == "":
            st.warning("Primero detecta o carga una imagen con texto.")
        else:
            result, output_text = text_to_speech(input_language, output_language, text, tld)
            with open(f"temp/{result}.mp3", "rb") as audio_file:
                audio_bytes = audio_file.read()

            st.markdown("## Audio generado:")
            st.audio(audio_bytes, format="audio/mp3", start_time=0)

            if display_output_text:
                st.markdown("## Texto traducido:")
                st.info(output_text)
