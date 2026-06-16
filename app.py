import json
import streamlit as st
from google import genai

st.set_page_config(page_title="AE Extractor", page_icon="💊", layout="centered")
st.title("💊 Adverse Event Extractor")
st.caption("Paste a free-text adverse event report — get structured fields and a draft narrative.")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

report = st.text_area("Adverse event report", height=180,
                      placeholder="e.g. A 67-year-old woman taking metformin developed severe nausea...")

if st.button("Extract", type="primary") and report:
    with st.spinner("Analysing report..."):
        prompt = f"""You are a pharmacovigilance assistant. From the report below, extract JSON with keys: drug, reactions (list), seriousness, outcome, patient_age, patient_sex. Use "not reported" for anything missing. Return ONLY JSON.

REPORT:
{report}
"""
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        text = resp.text.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        nprompt = f"Write a brief neutral clinical case narrative (3-4 sentences) from: {data}"
        narrative = client.models.generate_content(model="gemini-2.5-flash", contents=nprompt).text

    reactions = data.get("reactions", [])
    if isinstance(reactions, str):
        reactions = [reactions]

    st.divider()
    st.subheader("Extracted fields")
    c1, c2, c3 = st.columns(3)
    c1.metric("Drug", data.get("drug", "—"))
    c2.metric("Seriousness", data.get("seriousness", "—"))
    c3.metric("Patient", f'{data.get("patient_age","—")}, {data.get("patient_sex","—")}')
    st.write("**Reactions:** " + ", ".join(reactions))
    st.write("**Outcome:** " + str(data.get("outcome", "—")))

    st.divider()
    st.subheader("Draft narrative")
    st.write(narrative)

st.divider()
st.caption("Demo only — not for clinical or regulatory use. LLMs can misread or invent details, so every extraction needs human review.")
