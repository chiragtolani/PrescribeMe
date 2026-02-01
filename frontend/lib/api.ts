const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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

export async function analyzePrescription(
  prescriptionText: string,
  patientContext: string
): Promise<AnalyzeResponse> {
  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      prescription_text: prescriptionText,
      patient_context: patientContext,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Analysis failed");
  }
  return res.json();
}

export async function initKnowledgeBase(): Promise<InitKBResponse> {
  const res = await fetch(`${API_BASE}/api/init-kb`, { method: "POST" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Init failed");
  }
  return res.json();
}

export async function healthCheck(): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE}/api/health`);
  if (!res.ok) throw new Error("Backend unavailable");
  return res.json();
}
