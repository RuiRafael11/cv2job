import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "cv2job — Beat the ATS bots. Get the interview.",
  description:
    "cv2job is an AI résumé optimizer that scores your CV against any job description the way an ATS would — then rewrites it into a Harvard-format PDF that gets past the bots. €9 for 10 optimizations.",
  keywords: [
    "CV optimizer",
    "ATS resume",
    "resume optimizer",
    "AI resume",
    "Harvard resume",
    "job application",
    "cv2job",
  ],
  authors: [{ name: "Rui Rafael" }],
  openGraph: {
    title: "cv2job — Beat the ATS bots. Get the interview.",
    description:
      "AI résumé optimizer with a 4-dimension ATS score, keyword gap analysis, and Harvard-format PDF export.",
    url: "https://github.com/RuiRafael11/cv2job",
    siteName: "cv2job",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "cv2job — Beat the ATS bots. Get the interview.",
    description:
      "AI résumé optimizer with a 4-dimension ATS score, keyword gap analysis, and Harvard-format PDF export.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased bg-background text-foreground">
        {children}
      </body>
    </html>
  );
}
