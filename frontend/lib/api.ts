/** Base URL for the API (no trailing slash). */
const API_BASE = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/+$/, "");

/** Request timeout in ms (backend may take 30–90s for retrieval + LLM). */
const ANALYZE_TIMEOUT_MS = Number(process.env.NEXT_PUBLIC_ANALYZE_TIMEOUT_MS) || 90000;

/** Init KB can take several minutes with a large dataset (embedding + Chroma upsert). */
const INIT_KB_TIMEOUT_MS = Number(process.env.NEXT_PUBLIC_INIT_KB_TIMEOUT_MS) || 300000;

export type RetrievedChunk = {
  id: string;
  score: number;
  document: string;
  metadata: {
    drug_a?: string;
    drug_b?: string;
    risk?: string;
    summary?: string;
    evidence?: string;
    alternatives?: string;
    confidence?: string;
  };
};

export type AnalyzeResponse = {
  assessment: string;
  retrieved: RetrievedChunk[];
};

export type InitKBResponse = {
  ok: boolean;
  message: string;
  count?: number;
};

function parseErrorDetail(res: Response, body: unknown): string {
  if (typeof body === "object" && body !== null && "detail" in body) {
    const d = (body as { detail?: string | string[] }).detail;
    if (typeof d === "string") return d;
    if (Array.isArray(d) && d.length) return d.map(String).join("; ");
  }
  if (res.status === 408 || res.status === 504) return "Request timed out. Please try again.";
  if (res.status === 429) return "Too many requests. Please wait a moment and try again.";
  if (res.status >= 500) return "Server error. Please try again in a moment.";
  return res.statusText || "Request failed.";
}

export async function analyzePrescription(
  prescriptionText: string,
  patientContext: string,
  signal?: AbortSignal
): Promise<AnalyzeResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), ANALYZE_TIMEOUT_MS);
  const abortSignal = signal ?? controller.signal;

  try {
    const res = await fetch(`${API_BASE}/api/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prescription_text: prescriptionText.trim(),
        patient_context: (patientContext || "").trim(),
      }),
      signal: abortSignal,
    });
    const body = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(parseErrorDetail(res, body));
    }
    return body as AnalyzeResponse;
  } catch (e) {
    if (e instanceof Error) {
      if (e.name === "AbortError") {
        throw new Error("Request took too long. Please try again.");
      }
      throw e;
    }
    throw new Error("Analysis failed.");
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function initKnowledgeBase(): Promise<InitKBResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), INIT_KB_TIMEOUT_MS);
  try {
    const res = await fetch(`${API_BASE}/api/init-kb`, {
      method: "POST",
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      if (res.status === 404) {
        throw new Error(
          "Init KB endpoint not found (404). Check NEXT_PUBLIC_API_URL and that the backend is deployed."
        );
      }
      throw new Error(err.detail || "Init failed");
    }
    return res.json();
  } catch (e) {
    clearTimeout(timeoutId);
    if (e instanceof Error) {
      if (e.name === "AbortError") {
        throw new Error("Initialize KB timed out. For large datasets, run from CLI: python -m scripts.build_kb");
      }
      throw e;
    }
    throw new Error("Init failed");
  }
}

export async function healthCheck(): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE}/api/health`);
  if (!res.ok) throw new Error("Backend unavailable");
  return res.json();
}
