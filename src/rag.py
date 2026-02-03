"""RAG pipeline: retrieve evidence and synthesize assessment."""
from src.llm import synthesize_assessment
from src.preprocessing import preprocess_patient_context, preprocess_prescription
from src.retrieval import retrieve_for_prescription


def run_analysis(
    prescription_text: str,
    patient_context: str = "",
):
    """Retrieve relevant evidence and synthesize risk assessment and recommendations.
    Inputs are preprocessed (cleaned, length-limited) before retrieval and LLM.
    """
    prescription_text = preprocess_prescription(prescription_text)
    patient_context = preprocess_patient_context(patient_context)

    if not prescription_text:
        return {
            "assessment": "Please enter at least one drug or prescription to analyze.",
            "retrieved": [],
            "error": None,
        }

    try:
        retrieved = retrieve_for_prescription(prescription_text, patient_context)
        assessment = synthesize_assessment(
            prescription_text=prescription_text,
            patient_context=patient_context,
            retrieved_chunks=retrieved,
        )
        return {
            "assessment": assessment,
            "retrieved": retrieved,
            "error": None,
        }
    except ValueError as e:
        return {
            "assessment": "",
            "retrieved": [],
            "error": str(e),
        }
    except Exception as e:
        return {
            "assessment": "",
            "retrieved": [],
            "error": str(e),
        }
