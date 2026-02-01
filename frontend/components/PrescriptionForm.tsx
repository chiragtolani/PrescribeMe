"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Search } from "lucide-react";

type Props = {
  onAnalyze: (prescription: string) => void;
  loading: boolean;
};

export default function PrescriptionForm({ onAnalyze, loading }: Props) {
  const [prescription, setPrescription] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if ((prescription || "").trim()) onAnalyze(prescription.trim());
  };

  return (
    <motion.form
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      onSubmit={handleSubmit}
      className="rounded-2xl border border-slate-200/80 bg-white/90 p-6 shadow-lg shadow-slate-200/50 backdrop-blur"
    >
      <label className="block">
        <span className="font-display text-sm font-semibold text-slate-700">
          Prescription to review
        </span>
        <textarea
          value={prescription}
          onChange={(e) => setPrescription(e.target.value)}
          placeholder="Enter drug names or prescription text (one per line or comma-separated)&#10;e.g. Warfarin 5 mg&#10;Aspirin 81 mg&#10;Omeprazole 20 mg"
          rows={5}
          disabled={loading}
          className="mt-3 w-full resize-y rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-800 placeholder:text-slate-400 focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 disabled:bg-slate-50 disabled:text-slate-500"
        />
      </label>
      <div className="mt-4 flex items-center gap-3">
        <motion.button
          type="submit"
          disabled={loading || !prescription.trim()}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="inline-flex items-center gap-2 rounded-xl bg-teal-600 px-6 py-3 font-semibold text-white shadow-lg shadow-teal-600/25 transition hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none"
        >
          {loading ? (
            <>
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Analyzing…
            </>
          ) : (
            <>
              <Search className="h-5 w-5" />
              Analyze prescription
            </>
          )}
        </motion.button>
        <span className="text-xs text-slate-500">
          Retrieves evidence and generates risk assessment.
        </span>
      </div>
    </motion.form>
  );
}
