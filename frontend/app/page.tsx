import Image from "next/image";
import Link from "next/link";
import { ArrowRight, Building2, ClipboardCheck, FileCheck2, ShieldCheck } from "lucide-react";

import { ProgressIndex } from "@/components/ProgressIndex";
import { fuzionBrand } from "@/lib/brand";

const platformSignals = [
  { label: "Building Profiles", value: "BUILD", icon: Building2 },
  { label: "Protection Passport", value: "PROTECT", icon: ShieldCheck },
  { label: "Closeout Scoring", value: "ADVISE", icon: FileCheck2 },
  { label: "Handover Operations", value: "Buildings Under Protection™", icon: ClipboardCheck }
];

export default function Home() {
  return (
    <main className="fop-blueprint fop-fade-in min-h-screen text-[color:var(--text-primary)]">
      <header className="flex min-h-16 items-center justify-between border-b border-[color:var(--border)] bg-white px-5 sm:px-8">
        <Link href="/" className="flex items-center gap-3">
          <Image src="/brand/fpp-logo.svg" alt={`${fuzionBrand.productName} logo`} width={240} height={70} priority className="h-auto w-[220px]" />
        </Link>
        <nav className="flex items-center gap-3 text-sm">
          <Link href="/dashboard" className="hidden text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)] sm:inline">{fuzionBrand.missionControlName}</Link>
          <Link href="/properties" className="hidden text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)] sm:inline">Properties</Link>
          <Link href="/buildings" className="hidden text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)] sm:inline">Buildings</Link>
          <Link href="/login" className="fop-button-primary h-10">
            Sign in
            <ArrowRight size={16} />
          </Link>
        </nav>
      </header>

      <section className="mx-auto grid min-h-[calc(100vh-4rem)] w-full max-w-7xl items-center gap-10 px-5 py-10 sm:px-8 lg:grid-cols-[1fr_460px]">
        <div className="max-w-3xl">
          <p className="fop-label">{fuzionBrand.product}</p>
          <h1 className="mt-5 text-4xl font-semibold tracking-normal text-[color:var(--text-primary)] sm:text-5xl lg:text-6xl">{fuzionBrand.missionControlSubtitle}</h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-[color:var(--text-secondary)]">
            FOP connects building profiles, closeout scoring, executive intelligence, and stewardship for Buildings Under Protection™.
          </p>
          <p className="mt-5 text-sm font-semibold tracking-[0.26em] text-[color:var(--fop-build-text)]">{fuzionBrand.tagline}</p>
          <p className="mt-3 text-sm text-[color:var(--text-secondary)]">{fuzionBrand.protectedMetric}</p>
          <div className="mt-8 max-w-2xl">
            <ProgressIndex score={88} label="FPP Progress Index™" size="lg" showDescriptions variant="dashboard" />
          </div>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/login" className="fop-button-primary h-12">
              Go to login
              <ArrowRight size={16} />
            </Link>
            <Link href="/dashboard" className="fop-button-secondary h-12">
              Continue to Mission Control
            </Link>
          </div>
        </div>

        <div className="rounded-2xl border border-[color:var(--border)] bg-white p-5 shadow-[0_18px_44px_rgba(15,23,42,0.08)]">
          <div className="flex items-center justify-between border-b border-[color:var(--border)] pb-4">
            <div>
              <p className="text-sm font-semibold text-[color:var(--text-primary)]">Release 1.0 Entry</p>
              <p className="mt-1 text-xs text-[color:var(--text-muted)]">{fuzionBrand.contractorSubtitle}</p>
            </div>
          </div>
          <div className="mt-5 grid gap-3">
            {platformSignals.map((signal) => {
              const Icon = signal.icon;
              return (
                <div key={signal.label} className="flex items-center justify-between rounded-lg border border-[color:var(--border)] bg-[color:var(--surface-elevated)] p-4">
                  <div className="flex items-center gap-3">
                    <Icon size={18} className="text-[color:var(--fop-build-text)]" />
                    <span className="text-sm font-medium text-[color:var(--text-primary)]">{signal.label}</span>
                  </div>
                  <span className="text-xs font-semibold uppercase tracking-[0.16em] text-[color:var(--text-muted)]">{signal.value}</span>
                </div>
              );
            })}
          </div>
        </div>
      </section>
    </main>
  );
}
