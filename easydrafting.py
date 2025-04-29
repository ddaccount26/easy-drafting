import streamlit as st
import os
import io
from google.cloud import vision
from google.cloud import translate_v2 as translate
from PIL import Image

# Load service account info from Streamlit secrets
gcp_service_account = dict(st.secrets["gcp_service_account"])

# Create a temporary credentials file from the secrets
import json
from tempfile import NamedTemporaryFile

with NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp_file:
    json.dump(gcp_service_account, tmp_file)
    tmp_file_path = tmp_file.name


# Set the GOOGLE_APPLICATION_CREDENTIALS env variable to the temp file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_file_path

# Now initialize Google Cloud clients
vision_client = vision.ImageAnnotatorClient()
translate_client = translate.Client()

# Initialize Google Cloud clients
try:
    vision_client = vision.ImageAnnotatorClient()
    translate_client = translate.Client()
except Exception as e:
    st.error(f"Failed to initialize Google Cloud clients: {e}")
    st.stop()

# UI setup
st.set_page_config(page_title="Bengali Image to English Text", layout="wide")
st.title("🖼️ Bengali Image → English Text Translator")

# Upload image
uploaded_file = st.file_uploader("Upload a Bengali image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    try:
        image = Image.open(uploaded_file)

        # Side-by-side layout
        col1, col2 = st.columns([1, 2])  # Image takes 1/3, text takes 2/3

        with col1:
            st.image(image, caption="Uploaded Image", use_container_width=True)

        with col2:
            # Convert image to bytes
            byte_stream = io.BytesIO()
            image.save(byte_stream, format="PNG")
            content = byte_stream.getvalue()

            # OCR
            image_obj = vision.Image(content=content)
            response = vision_client.text_detection(image=image_obj)
            texts = response.text_annotations

            if texts:
                original_text = texts[0].description
                translated = translate_client.translate(original_text, target_language="en")
                translated_text = translated["translatedText"]

                st.subheader("📃 Translated English Text")
                st.text_area(label="", value=translated_text, height=400)

                # Download button
                st.download_button(
                    label="⬇️ Download Translation",
                    data=translated_text,
                    file_name="translated_text.txt",
                    mime="text/plain"
                )
            else:
                st.warning("No text detected in the image.")

    except Exception as e:
        st.error(f"Error processing image: {e}")
