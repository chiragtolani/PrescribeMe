"""
PrescribeMe — Prescription Risk & Drug Interaction Intelligence Agent
Streamlit entrypoint.
"""
import streamlit as st

from config import CHROMA_COLLECTION_NAME
from src.chroma_store import build_and_populate_store, get_chroma_client
from src.rag import run_analysis

# Page config
st.set_page_config(
    page_title="PrescribeMe — Drug Interaction Intelligence",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a clean, clinical, interactive UI
st.markdown(
    """
    <style>
    /* Typography and layout */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Header area */
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.15);
    }
    .main-header h1 {
        margin: 0;
        font-size: 1.75rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 0.95rem;
    }
    
    /* Cards and containers */
    .stExpander {
        background: white;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    [data-testid="stExpander"] {
        background: white;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }
    
    /* Buttons */
    .stButton > button {
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 1.25rem;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebar"] .stMarkdown {
        font-weight: 600;
        color: #334155;
    }
    
    /* Risk badges (used in markdown) */
    .risk-high { background: #fef2f2; color: #b91c1c; padding: 0.2em 0.5em; border-radius: 6px; font-weight: 600; }
    .risk-moderate { background: #fffbeb; color: #b45309; padding: 0.2em 0.5em; border-radius: 6px; font-weight: 600; }
    .risk-low { background: #f0fdf4; color: #15803d; padding: 0.2em 0.5em; border-radius: 6px; font-weight: 600; }
    .risk-contraindicated { background: #fef2f2; color: #991b1b; padding: 0.2em 0.5em; border-radius: 6px; font-weight: 700; }
    
    /* Info box */
    .info-callout {
        background: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 1rem 1.25rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        font-size: 0.9rem;
        color: #1e40af;
    }
    
    /* Result block */
    .result-block {
        background: white;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def ensure_knowledge_base():
    """Initialize Chroma with sample data if not already populated."""
    try:
        client = get_chroma_client()
        coll = client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"description": "PrescribeMe drug interaction evidence"},
        )
        if coll.count() > 0:
            return True, None
    except Exception:
        pass
    try:
        build_and_populate_store()
        return True, None
    except Exception as e:
        return False, str(e)


def main():
    # Header
    st.markdown(
        """
        <div class="main-header">
            <h1>💊 PrescribeMe</h1>
            <p>Prescription Risk & Drug Interaction Intelligence — evidence-backed, context-aware decision support.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar: Patient context and setup
    with st.sidebar:
        st.markdown("### 🧑‍⚕️ Patient context")
        st.caption("Optional. Improves relevance of interaction analysis.")
        age = st.number_input("Age (years)", min_value=1, max_value=120, value=40, step=1)
        weight_kg = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=70.0, step=0.5)
        conditions = st.text_area(
            "Relevant conditions (e.g. renal impairment, hypertension)",
            height=80,
            placeholder="e.g. CKD stage 3, hypertension",
        )
        current_meds = st.text_area(
            "Current medications (comma or newline separated)",
            height=100,
            placeholder="e.g. Lisinopril 10 mg, Metformin 500 mg",
        )

        st.divider()
        st.markdown("### ⚙️ Setup")
        if st.button("Initialize knowledge base", help="Load sample drug interaction data into the vector store. Run once."):
            with st.spinner("Building knowledge base..."):
                ok, err = ensure_knowledge_base()
                if ok:
                    st.success("Knowledge base ready.")
                else:
                    st.error(f"Failed: {err}")

    # Build patient context string for RAG
    patient_context_parts = [f"Age: {age} years", f"Weight: {weight_kg} kg"]
    if (conditions or "").strip():
        patient_context_parts.append(f"Conditions: {conditions.strip()}")
    if (current_meds or "").strip():
        patient_context_parts.append(f"Current medications: {current_meds.strip()}")
    patient_context = "; ".join(patient_context_parts)

    # Main: Prescription input and analysis
    st.markdown("#### 📋 Prescription to review")
    prescription = st.text_area(
        "Enter drug names or prescription text (one per line or comma-separated)",
        height=120,
        placeholder="e.g. Warfarin 5 mg\nAspirin 81 mg\nOmeprazole 20 mg",
        label_visibility="collapsed",
    )

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        analyze_clicked = st.button("🔍 Analyze prescription", type="primary", use_container_width=True)
    with col2:
        st.caption("Retrieves evidence and generates risk assessment.")

    if analyze_clicked:
        if not (prescription or "").strip():
            st.warning("Please enter at least one drug or prescription text.")
        else:
            with st.spinner("Retrieving evidence and synthesizing assessment..."):
                result = run_analysis(
                    prescription_text=prescription.strip(),
                    patient_context=patient_context,
                )

            if result["error"]:
                st.error(f"Analysis failed: {result['error']}")
                st.info("Ensure OPENAI_API_KEY is set in .env and the knowledge base is initialized (sidebar).")
            else:
                st.markdown("---")
                st.markdown("#### 📊 Assessment")
                st.markdown(
                    '<div class="result-block">',
                    unsafe_allow_html=True,
                )
                st.markdown(result["assessment"])
                st.markdown("</div>", unsafe_allow_html=True)

                if result["retrieved"]:
                    st.markdown("#### 📚 Retrieved evidence")
                    st.caption("Sources used to ground the assessment. Expand to see details.")
                    for i, chunk in enumerate(result["retrieved"], 1):
                        meta = chunk.get("metadata") or {}
                        drug_a = meta.get("drug_a", "")
                        drug_b = meta.get("drug_b", "")
                        risk = (meta.get("risk") or "").lower()
                        with st.expander(f"**{drug_a} + {drug_b}** — risk: {risk} (relevance: {chunk.get('score', 0):.2f})"):
                            st.markdown(f"**Summary:** {meta.get('summary', '—')}")
                            st.markdown(f"**Evidence:** {meta.get('evidence', '—')}")
                            st.markdown(f"**Alternatives:** {meta.get('alternatives', '—')}")

    # Footer callout
    st.markdown("---")
    st.markdown(
        """
        <div class="info-callout">
            <strong>PrescribeMe</strong> is a decision-support tool, not a replacement for clinical judgement. 
            It prioritizes transparency, safety, and explainability. Always verify with authoritative drug references and clinical guidelines.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
