import json
import streamlit as st
from google import genai

st.title("Adverse Event Extractor")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

report = st.text_area("Paste an adverse event report", height=180)

if st.button("Extract") and report:
    prompt = f"""You are a pharmacovigilance assistant. From the report below, extract JSON with keys: drug, reactions (list), seriousness, outcome, patient_age, patient_sex. Use "not reported" for anything missing. Return ONLY JSON.

REPORT:
{report}
"""
    resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    text = resp.text.strip().replace("```json", "").replace("```", "").strip()
    data = json.loads(text)
    st.subheader("Extracted fields")
    st.json(data)

    nprompt = f"Write a brief neutral clinical case narrative (3-4 sentences) from: {data}"
    narrative = client.models.generate_content(model="gemini-2.5-flash", contents=nprompt).text
    st.subheader("Draft narrative")
    st.write(narrative)

st.caption("Demo only - not for clinical or regulatory use. LLMs can misread or invent details, so every extraction needs human review.")
