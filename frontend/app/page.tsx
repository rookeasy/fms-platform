import Image from "next/image";
import Link from "next/link";
import { ArrowRight, Building2, ClipboardCheck, FileCheck2, ShieldCheck } from "lucide-react";

import { ProgressIndex } from "@/components/ProgressIndex";
import { fuzionBrand } from "@/lib/brand";

const platformSignals = [
  { label: "Building Profiles", value: "Build", icon: Building2 },
  { label: "Protection Passport", value: "Protect", icon: ShieldCheck },
  { label: "Closeout Scoring", value: "Advise", icon: FileCheck2 },
  { label: "Handover Operations", value: "Sustain", icon: ClipboardCheck }
];

export default function Home() {
  return (
    <main className="fop-blueprint fop-fade-in min-h-screen bg-[#050A18] text-white">
      <header className="flex min-h-16 items-center justify-between border-b border-white/10 px-5 sm:px-8">
        <Link href="/" className="flex items-center gap-3">
          <Image src="/brand/fpp-mark.svg" alt={`${fuzionBrand.productName} logo`} width={40} height={40} priority />
          <span>
            <span className="block text-sm font-semibold tracking-[0.18em]">{fuzionBrand.shortName}</span>
            <span className="block text-xs text-slate-400">{fuzionBrand.companyName}</span>
          </span>
        </Link>
        <nav className="flex items-center gap-3 text-sm">
          <Link href="/dashboard" className="hidden text-slate-300 hover:text-white sm:inline">Mission Control</Link>
          <Link href="/properties" className="hidden text-slate-300 hover:text-white sm:inline">Properties</Link>
          <Link href="/buildings" className="hidden text-slate-300 hover:text-white sm:inline">Buildings</Link>
          <Link href="/login" className="inline-flex h-10 items-center gap-2 rounded-xl bg-[#FF6B5F] px-4 font-semibold text-[#050A18]">
            Sign in
            <ArrowRight size={16} />
          </Link>
        </nav>
      </header>

      <section className="mx-auto grid min-h-[calc(100vh-4rem)] w-full max-w-7xl items-center gap-10 px-5 py-10 sm:px-8 lg:grid-cols-[1fr_460px]">
        <div className="max-w-3xl">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-[#FFB4AD]">Fuzion Protection Platform</p>
          <h1 className="mt-5 text-4xl font-semibold tracking-normal text-white sm:text-5xl lg:text-6xl">{fuzionBrand.subtitle}</h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-slate-300">
            {fuzionBrand.productName} connects building profiles, closeout scoring, and handover operations for owners, contractors, and property teams.
          </p>
          <p className="mt-5 text-sm font-semibold tracking-[0.26em] text-[#FF6B5F]">{fuzionBrand.tagline}</p>
          <div className="mt-8 max-w-2xl">
            <ProgressIndex score={88} label="FPP Progress Index™" size="lg" showDescriptions variant="dashboard" />
          </div>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/login" className="inline-flex h-12 items-center gap-2 rounded-xl bg-[#FF6B5F] px-5 text-sm font-semibold text-[#050A18] hover:bg-[#FF857B]">
              Go to login
              <ArrowRight size={16} />
            </Link>
            <Link href="/dashboard" className="inline-flex h-12 items-center rounded-xl border border-white/15 px-5 text-sm font-semibold text-white hover:bg-white/10">
              Continue to Mission Control
            </Link>
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-white/[0.07] p-5 shadow-[0_24px_80px_rgba(0,0,0,0.4)] backdrop-blur-xl">
          <div className="flex items-center justify-between border-b border-white/10 pb-4">
            <div>
              <p className="text-sm font-semibold">Release 1.0 Entry</p>
              <p className="mt-1 text-xs text-slate-400">{fuzionBrand.contractorSubtitle}</p>
            </div>
            <Image src="/brand/fpp-mark.svg" alt="" width={42} height={42} />
          </div>
          <div className="mt-5 grid gap-3">
            {platformSignals.map((signal) => {
              const Icon = signal.icon;
              return (
                <div key={signal.label} className="flex items-center justify-between rounded-xl border border-white/10 bg-[#050A18]/70 p-4">
                  <div className="flex items-center gap-3">
                    <Icon size={18} className="text-[#FFB4AD]" />
                    <span className="text-sm font-medium">{signal.label}</span>
                  </div>
                  <span className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">{signal.value}</span>
                </div>
              );
            })}
          </div>
        </div>
      </section>
    </main>
  );
}
