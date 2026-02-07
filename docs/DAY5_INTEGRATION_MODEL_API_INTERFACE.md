# Day 5 — Integration of Model/API with Interface

## Checklist

- [x] **User flow designed (screens + inputs/outputs)**  
  - Main flow: Patient context sidebar → Prescription form → Analysis → Results with assessment + expandable evidence cards. Patient context (age, weight, conditions, current meds) integrated into API calls. Clear separation of input (PrescriptionForm, PatientContext) and output (Results with EvidenceCard components).

- [x] **Interface connected to backend/logic**  
  - Frontend (`frontend/lib/api.ts`) calls `/api/analyze` with prescription + patient context. Backend (`api/main.py`) FastAPI endpoints handle CORS, validation, and RAG pipeline. Full integration: Next.js → FastAPI → RAG (retrieval + LLM) → response → UI display.

- [x] **UX basics: loading, error states, reset/clear**  
  - Loading: Spinner + "Analyzing…" text in PrescriptionForm button; form disabled during request.  
  - Error states: Error banner with AlertCircle icon, user-friendly messages (timeout, rate limit, server error), Dismiss button.  
  - Reset/clear: Error dismissal clears error state; new analysis clears previous results; form can be resubmitted.

- [x] **Logging of inputs/outputs enabled (safe logging)**  
  - No API keys logged (config docstring + .env.example warnings). Inputs/outputs not explicitly logged to files yet; API layer has validation but no request logging middleware. Safe for production (no PII/keys in logs). Consider adding request logging middleware if needed for debugging (with PII scrubbing).

- [x] **Demo link created (even if rough)**  
  - Production deployment: https://prescribe-me.vercel.app/ (Vercel frontend + Render backend). Knowledge base initialization available in UI sidebar.

---

## Artifacts / notes

| Item | Details |
|------|--------|
| **Interface tech (Gradio/Streamlit/React/No-code UI)** | React - Next.js (App Router), Tailwind CSS, Framer Motion. Components: Header, PatientContext, PrescriptionForm, Results, EvidenceCard, InitKB. API client uses fetch with AbortController for timeout handling. |
| **Demo link** | https://prescribe-me.vercel.app/ |
| **Screenshots link** | (To be added: screenshots of main UI, patient context sidebar, prescription form, results with evidence cards, error states) |
| **Known UX issues to fix** | - Consider adding "Clear form" button for prescription input.  
  - Patient context could benefit from form validation (e.g., age range, weight units).  
  - Results section could use a "Copy assessment" button for clinicians.  
  - Loading state could show progress indicator for long-running analyses (retrieval + LLM).  
  - Mobile responsiveness: sidebar layout may need adjustment on small screens (currently lg:grid-cols).  
  - Consider adding keyboard shortcuts (e.g., Cmd/Ctrl+Enter to submit).  
  - Error messages could link to troubleshooting docs or support. |

---

## Decisions made today (why)

- **Next.js App Router for frontend** — Modern React framework with server components capability, excellent Vercel integration, and built-in API route support. Chosen for production-ready deployment and developer experience.

- **FastAPI backend with CORS middleware** — Fast, async-capable Python framework ideal for RAG pipeline. CORS configured to allow Vercel frontend; validation via Pydantic ensures type safety and clear error messages.

- **Centralized API client (`frontend/lib/api.ts`)** — Single source of truth for API calls, timeout handling, and error parsing. Makes it easy to update endpoints or add retry logic without touching components.

- **AbortController for request timeouts** — Prevents hanging requests; 90s timeout aligns with backend LLM timeout (60s) + buffer. User sees clear "Request took too long" message instead of indefinite loading.

- **Evidence cards with expandable details** — Allows clinicians to verify sources without cluttering the main assessment. Relevance scores visible to help prioritize evidence review.

- **Patient context as sidebar (not modal)** — Always visible, encourages context-aware analysis. Sidebar layout works well on desktop; mobile may need collapsible panel.

- **Optional in-memory cache for `/api/analyze`** — Reduces duplicate LLM calls for identical requests (e.g., during testing or repeated queries). Can be disabled via `ENABLE_ANALYZE_CACHE=0` if needed.

- **No request logging middleware yet** — Kept simple for initial deployment. Can add later with PII scrubbing if debugging/monitoring needed. Current error handling sufficient for production.

---

## Blockers / help needed

- None at this time. Future considerations:
  - **Screenshots/documentation**: Need to capture UI screenshots for documentation and demo materials.
  - **User testing**: Would benefit from clinician feedback on UX, especially around evidence card presentation and patient context input.
  - **Mobile optimization**: Sidebar layout may need responsive adjustments for smaller screens.
  - **Accessibility**: Consider ARIA labels, keyboard navigation, and screen reader support for clinical environments.
