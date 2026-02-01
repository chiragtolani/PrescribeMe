"use client";

import { motion } from "framer-motion";
import { Pill } from "lucide-react";

export default function Header() {
  return (
    <motion.header
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-teal-900/90 to-slate-900 text-white shadow-xl shadow-teal-900/20"
    >
      {/* Subtle medical pattern overlay */}
      <div
        className="absolute inset-0 opacity-[0.07]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 0h2v40H0V0zm4 0h2v40H4V0zm4 0h2v40H8V0zm4 0h2v40h-2V0zm4 0h2v40h-2V0zm4 0h2v40h-2V0zm4 0h2v40h-2V0zm4 0h2v40h-2V0z' fill='%23fff' fill-opacity='1' fill-rule='evenodd'/%3E%3C/svg%3E")`,
        }}
      />
      <div className="relative flex items-center gap-4 px-8 py-6">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.15, type: "spring", stiffness: 200 }}
          className="flex h-14 w-14 items-center justify-center rounded-xl bg-white/10 backdrop-blur"
        >
          <Pill className="h-8 w-8 text-teal-300" />
        </motion.div>
        <div>
          <h1 className="font-display text-2xl font-bold tracking-tight md:text-3xl">
            PrescribeMe
          </h1>
          <p className="mt-1 text-sm text-slate-300 md:text-base">
            Prescription Risk & Drug Interaction Intelligence — evidence-backed, context-aware decision support.
          </p>
        </div>
      </div>
    </motion.header>
  );
}
