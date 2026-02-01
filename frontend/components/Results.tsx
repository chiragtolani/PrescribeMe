"use client";

import { motion } from "framer-motion";
import { ClipboardList, BookOpen } from "lucide-react";
import EvidenceCard from "./EvidenceCard";
import type { RetrievedChunk } from "@/lib/api";

type Props = {
  assessment: string;
  retrieved: RetrievedChunk[];
};

export default function Results({ assessment, retrieved }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      <section className="rounded-2xl border border-slate-200/80 bg-white/90 p-6 shadow-lg shadow-slate-200/50 backdrop-blur">
        <div className="flex items-center gap-3 text-slate-800">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-50 text-teal-600">
            <ClipboardList className="h-5 w-5" />
          </div>
          <h2 className="font-display text-lg font-semibold">Assessment</h2>
        </div>
        <div className="mt-4 rounded-xl bg-slate-50/80 p-5 text-sm leading-relaxed text-slate-700 whitespace-pre-wrap">
          {assessment}
        </div>
      </section>

      {retrieved.length > 0 && (
        <section>
          <div className="flex items-center gap-3 text-slate-800">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-50 text-teal-600">
              <BookOpen className="h-5 w-5" />
            </div>
            <div>
              <h2 className="font-display text-lg font-semibold">
                Retrieved evidence
              </h2>
              <p className="text-xs text-slate-500">
                Sources used to ground the assessment. Expand to see details.
              </p>
            </div>
          </div>
          <ul className="mt-4 space-y-3">
            {retrieved.map((chunk, i) => (
              <li key={chunk.id}>
                <EvidenceCard chunk={chunk} index={i} />
              </li>
            ))}
          </ul>
        </section>
      )}
    </motion.div>
  );
}
