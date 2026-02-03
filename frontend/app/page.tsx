"use client";

import { useState, useCallback } from "react";
import { motion } from "framer-motion";
import { AlertCircle } from "lucide-react";
import Header from "@/components/Header";
import PatientContext, {
  patientContextToApiString,
  type PatientContextValues,
} from "@/components/PatientContext";
import PrescriptionForm from "@/components/PrescriptionForm";
import Results from "@/components/Results";
import InitKB from "@/components/InitKB";
import { analyzePrescription } from "@/lib/api";

const defaultPatient: PatientContextValues = {
  age: 40,
  weightKg: 70,
  conditions: "",
  currentMeds: "",
};

export default function Home() {
  const [patient, setPatient] = useState<PatientContextValues>(defaultPatient);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{
    assessment: string;
    retrieved: { id: string; score: number; document: string; metadata: Record<string, string> }[];
  } | null>(null);

  const handleAnalyze = useCallback(
    async (prescription: string) => {
      setError(null);
      setResult(null);
      setLoading(true);
      try {
        const patientContext = patientContextToApiString(patient);
        const data = await analyzePrescription(prescription, patientContext);
        setResult({
          assessment: data.assessment,
          retrieved: data.retrieved,
        });
      } catch (e) {
        setError(e instanceof Error ? e.message : "Analysis failed.");
      } finally {
        setLoading(false);
      }
    },
    [patient]
  );

  return (
    <div className="min-h-screen">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <Header />

        <div className="mt-8 grid gap-8 lg:grid-cols-[320px_1fr] lg:grid-flow-col">
          {/* Sidebar — patient context & setup */}
          <aside className="space-y-6 lg:order-1 order-2">
            <PatientContext values={patient} onChange={setPatient} />
            <InitKB />
          </aside>

          {/* Main — prescription form & results */}
          <main className="min-w-0 lg:order-2 order-1">
            <PrescriptionForm onAnalyze={handleAnalyze} loading={loading} />

            {error && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-6 flex flex-wrap items-center gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-red-800"
              >
                <AlertCircle className="h-5 w-5 shrink-0" />
                <p className="min-w-0 flex-1 text-sm">{error}</p>
                <button
                  type="button"
                  onClick={() => {
                    setError(null);
                    setResult(null);
                  }}
                  className="shrink-0 rounded-lg border border-red-300 bg-white px-3 py-1.5 text-sm font-medium text-red-700 transition hover:bg-red-100"
                >
                  Dismiss
                </button>
              </motion.div>
            )}

            {result && (
              <div className="mt-8">
                <Results
                  assessment={result.assessment}
                  retrieved={result.retrieved}
                />
              </div>
            )}
          </main>
        </div>

        {/* Footer disclaimer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-12 rounded-xl border-l-4 border-teal-500 bg-teal-50/80 px-5 py-4 text-sm text-teal-900"
        >
          <strong>PrescribeMe</strong> is a decision-support tool, not a
          replacement for clinical judgement. It prioritizes transparency,
          safety, and explainability. Always verify with authoritative drug
          references and clinical guidelines.
        </motion.footer>
      </div>
    </div>
  );
}
