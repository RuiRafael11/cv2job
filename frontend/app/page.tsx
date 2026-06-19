"use client";

import { useEffect } from "react";
import { Navbar } from "@/components/landing/Navbar";
import { Hero } from "@/components/landing/Hero";
import { TrustBar } from "@/components/landing/TrustBar";
import { Problem } from "@/components/landing/Problem";
import { Features } from "@/components/landing/Features";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { AtsDemo } from "@/components/landing/AtsDemo";
import { Pricing } from "@/components/landing/Pricing";
import { FAQ } from "@/components/landing/FAQ";
import { FinalCTA } from "@/components/landing/FinalCTA";
import { Footer } from "@/components/landing/Footer";

export default function Home() {
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const sessionToken = params.get("session_token") || params.get("checkout_session_id");
    if (sessionToken) {
      window.location.replace(`/app?session_token=${encodeURIComponent(sessionToken)}`);
    }
  }, []);

  return (
    <div className="relative min-h-screen flex flex-col bg-background">
      <Navbar />
      <main className="flex-1">
        <Hero />
        <TrustBar />
        <Problem />
        <Features />
        <HowItWorks />
        <AtsDemo />
        <Pricing />
        <FAQ />
        <FinalCTA />
      </main>
      <Footer />
    </div>
  );
}
