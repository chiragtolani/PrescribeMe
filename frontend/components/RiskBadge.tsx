"use client";

import { clsx } from "clsx";

type Props = {
  risk: string;
  className?: string;
};

export default function RiskBadge({ risk, className }: Props) {
  const r = (risk || "").toLowerCase();
  const styles = clsx(
    "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold",
    (r === "high" || r === "contraindicated") &&
      "bg-red-100 text-red-800 border border-red-200",
    r === "moderate" && "bg-amber-100 text-amber-800 border border-amber-200",
    r === "low" && "bg-emerald-100 text-emerald-800 border border-emerald-200",
    !["high", "moderate", "low", "contraindicated"].includes(r) &&
      "bg-slate-100 text-slate-700 border border-slate-200",
    className
  );
  return <span className={styles}>{risk || "—"}</span>;
}
