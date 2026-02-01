"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, FileText } from "lucide-react";
import RiskBadge from "./RiskBadge";
import type { RetrievedChunk } from "@/lib/api";

type Props = {
  chunk: RetrievedChunk;
  index: number;
};

export default function EvidenceCard({ chunk, index }: Props) {
  const [open, setOpen] = useState(false);
  const meta = chunk.metadata || {};
  const drugA = meta.drug_a || "";
  const drugB = meta.drug_b || "";
  const risk = meta.risk || "";
  const score = chunk.score ?? 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition-shadow hover:shadow-md"
    >
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between gap-3 px-5 py-4 text-left transition-colors hover:bg-slate-50/80"
      >
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal-50 text-teal-600">
            <FileText className="h-5 w-5" />
          </div>
          <div>
            <span className="font-semibold text-slate-800">
              {drugA} + {drugB}
            </span>
            <div className="mt-1 flex items-center gap-2">
              <RiskBadge risk={risk} />
              <span className="text-xs text-slate-500">
                relevance: {(score * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </div>
        <motion.span
          animate={{ rotate: open ? 180 : 0 }}
          className="text-slate-400"
        >
          <ChevronDown className="h-5 w-5" />
        </motion.span>
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="border-t border-slate-100 bg-slate-50/50"
          >
            <div className="space-y-4 px-5 py-4">
              {meta.summary && (
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                    Summary
                  </p>
                  <p className="mt-1 text-sm text-slate-700">{meta.summary}</p>
                </div>
              )}
              {meta.evidence && (
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                    Evidence
                  </p>
                  <p className="mt-1 text-sm text-slate-700">{meta.evidence}</p>
                </div>
              )}
              {meta.alternatives && (
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                    Alternatives
                  </p>
                  <p className="mt-1 text-sm text-slate-700">{meta.alternatives}</p>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
