import streamlit as st 
from pathlib import Path
import google.generativeai as genai 
from api_key import api_key
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# Configure genai with API key
genai.configure(api_key=api_key)

# Setup the model configuration
generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

# Apply safety settings
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

# System prompt
system_prompt = """
As a highly skilled medical practitioner specializing in image analysis, you are tasked with examining medical images for a renowned hospital. Your expertise is crucial in identifying any anomalies, diseases, or health issues that may be present in the images.
Your Responsibilities include:

1. Detailed Analysis: Thoroughly analyze each image, focusing on identifying any abnormal findings.
2. Findings Report: Document all observed anomalies or signs of disease. Clearly articulate these findings in a structured format.
3. Recommendations and Next Steps: Based on your analysis, suggest potential next steps, including further tests or treatments as applicable.
4. Treatment Suggestions: If appropriate, recommend possible treatment options or intervention

Important Notes:

1. Scope of Response: Only respond if the image pertains to human health issues.
2. Clarity of Image: In cases where the image quality impedes clear analysis, note that certain aspects are 'Unable to be determined based on the provided image.'
3. Disclaimer: Accompany your analysis with the disclaimer: "Consult with a Doctor before making any decision."

4. Your insights are invaluable in guiding clinical decisions. Please proceed with the analysis, adhering to the structured approach outlined above.

please provide me output response with these 4 headings Detailed Analysis,Findings Report, Recommendation and Next Steps, Treatment Suggestion, Disclaimer.
"""

# Model configuration with the correct model name
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings
)

# PDF creation helper function
def create_pdf(text):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40
    for line in text.split('\n'):
        if y < 40:
            c.showPage()
            y = height - 40
        c.drawString(40, y, line)
        y -= 15
    c.save()
    buffer.seek(0)
    return buffer

# Set Streamlit page config
st.set_page_config(page_title="Medical Skin Image Analytics", page_icon="👩‍⚕️")

# Display logo
st.image("mk_logo.png", width=100)

# Set the title and subheader
st.title("Medical Skin ❤️ Image Analytics📊👩‍⚕️")
st.subheader("An application that can help users to identify medical images")

# File uploader
uploaded_file = st.file_uploader("Upload the medical image for analysis", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.image(uploaded_file,width=300, caption="Uploaded Medical Image")
    

# Generate button
submit_button = st.button("Generate the Analysis")

# When button is clicked
if submit_button:
    if uploaded_file is not None:
        # Prepare image for API
        image_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": image_data
            }
        ]

        # Prepare the prompt
        prompt_parts = [
            image_parts[0],
            system_prompt
        ]

        # Generate content from Gemini
        
        response = model.generate_content(prompt_parts)
        if response:
            st.title("📊 Here is the analysis based on your image: ")
            

        # Display the response in the Streamlit app
            st.markdown("### 🧾 Analysis Result:")
            st.write(response.text)

        # Generate PDF
            pdf_data = create_pdf(response.text)

        # PDF download button
            st.download_button(
                label="📄 Download Report as PDF",
                data=pdf_data,
                file_name="medical_analysis_report.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("⚠️ Please upload a medical image before clicking the button.")
