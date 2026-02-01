"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Database, Loader2 } from "lucide-react";
import { initKnowledgeBase } from "@/lib/api";

type Props = {
  onSuccess?: () => void;
};

export default function InitKB({ onSuccess }: Props) {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const handleInit = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const res = await initKnowledgeBase();
      setMessage({
        type: "success",
        text: res.count ? `Knowledge base ready (${res.count} interactions).` : res.message,
      });
      onSuccess?.();
    } catch (e) {
      setMessage({
        type: "error",
        text: e instanceof Error ? e.message : "Failed to initialize.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="rounded-xl border border-slate-200/80 bg-white/80 p-4 shadow-sm backdrop-blur"
    >
      <div className="flex items-center gap-2 text-slate-700">
        <Database className="h-4 w-4 text-teal-600" />
        <span className="text-sm font-medium">Setup</span>
      </div>
      <p className="mt-1 text-xs text-slate-500">
        Load sample drug interaction data into the vector store. Run once.
      </p>
      <motion.button
        type="button"
        onClick={handleInit}
        disabled={loading}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="mt-3 inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:opacity-50"
      >
        {loading ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Initializing…
          </>
        ) : (
          "Initialize knowledge base"
        )}
      </motion.button>
      {message && (
        <p
          className={`mt-2 text-xs ${
            message.type === "success" ? "text-emerald-600" : "text-red-600"
          }`}
        >
          {message.text}
        </p>
      )}
    </motion.div>
  );
}
