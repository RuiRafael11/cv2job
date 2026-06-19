import type { Metadata } from "next";
import { Inter, Playfair_Display, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const playfair = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin"],
  display: "swap",
  weight: ["400", "500", "600", "700", "800", "900"],
  style: ["normal", "italic"],
});

const plexMono = IBM_Plex_Mono({
  variable: "--font-plex-mono",
  subsets: ["latin"],
  display: "swap",
  weight: ["400", "500", "600"],
});

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
      <body
        className={`${inter.variable} ${playfair.variable} ${plexMono.variable} antialiased bg-background text-foreground`}
      >
        {children}
        <Toaster />
      </body>
    </html>
  );
}
