import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-outfit",
  display: "swap",
});

export const metadata: Metadata = {
  title: "PrescribeMe — Drug Interaction Intelligence",
  description:
    "Evidence-backed prescription review: identify drug interactions and safer alternatives.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={outfit.variable}>
      <body className="min-h-screen font-sans antialiased bg-medical-pattern bg-medical-mesh">
        {children}
      </body>
    </html>
  );
}
