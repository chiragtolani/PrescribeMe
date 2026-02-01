"use client";

import { motion } from "framer-motion";
import { User } from "lucide-react";

export type PatientContextValues = {
  age: number;
  weightKg: number;
  conditions: string;
  currentMeds: string;
};

type Props = {
  values: PatientContextValues;
  onChange: (values: PatientContextValues) => void;
};

export default function PatientContext({ values, onChange }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
      className="rounded-xl border border-slate-200/80 bg-white/80 p-5 shadow-sm backdrop-blur"
    >
      <div className="flex items-center gap-2 text-slate-700">
        <User className="h-5 w-5 text-teal-600" />
        <h3 className="font-display font-semibold">Patient context</h3>
      </div>
      <p className="mt-1 text-xs text-slate-500">
        Optional — improves relevance of interaction analysis.
      </p>
      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <label className="block">
          <span className="text-sm font-medium text-slate-600">Age (years)</span>
          <input
            type="number"
            min={1}
            max={120}
            value={values.age}
            onChange={(e) =>
              onChange({ ...values, age: parseInt(e.target.value, 10) || 40 })
            }
            className="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20"
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-600">Weight (kg)</span>
          <input
            type="number"
            min={20}
            max={300}
            step={0.5}
            value={values.weightKg}
            onChange={(e) =>
              onChange({
                ...values,
                weightKg: parseFloat(e.target.value) || 70,
              })
            }
            className="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20"
          />
        </label>
      </div>
      <label className="mt-4 block">
        <span className="text-sm font-medium text-slate-600">Relevant conditions</span>
        <textarea
          rows={2}
          value={values.conditions}
          onChange={(e) => onChange({ ...values, conditions: e.target.value })}
          placeholder="e.g. CKD stage 3, hypertension"
          className="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm placeholder:text-slate-400 focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20"
        />
      </label>
      <label className="mt-4 block">
        <span className="text-sm font-medium text-slate-600">Current medications</span>
        <textarea
          rows={3}
          value={values.currentMeds}
          onChange={(e) => onChange({ ...values, currentMeds: e.target.value })}
          placeholder="e.g. Lisinopril 10 mg, Metformin 500 mg"
          className="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm placeholder:text-slate-400 focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20"
        />
      </label>
    </motion.div>
  );
}

export function patientContextToApiString(v: PatientContextValues): string {
  const parts = [`Age: ${v.age} years`, `Weight: ${v.weightKg} kg`];
  if (v.conditions.trim()) parts.push(`Conditions: ${v.conditions.trim()}`);
  if (v.currentMeds.trim()) parts.push(`Current medications: ${v.currentMeds.trim()}`);
  return parts.join("; ");
}
