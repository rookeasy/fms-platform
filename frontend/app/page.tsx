import Link from "next/link";
import { ArrowRight, Building2, ClipboardCheck, FileCheck2, ShieldCheck } from "lucide-react";

const platformSignals = [
  { label: "Building Registry", value: "Active", icon: Building2 },
  { label: "Protection Passport", value: "Ready", icon: ShieldCheck },
  { label: "Digital Closeout", value: "Scored", icon: FileCheck2 },
  { label: "Property Operations", value: "Live", icon: ClipboardCheck }
];

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <header className="flex min-h-16 items-center justify-between border-b border-white/10 px-5 sm:px-8">
        <Link href="/" className="flex items-center gap-3">
          <span className="flex h-9 w-9 items-center justify-center rounded-md bg-red-700 text-sm font-semibold">F</span>
          <span>
            <span className="block text-sm font-semibold">FOP</span>
            <span className="block text-xs text-slate-300">Fuzion Operations Platform</span>
          </span>
        </Link>
        <nav className="flex items-center gap-3 text-sm">
          <Link href="/dashboard" className="hidden text-slate-300 hover:text-white sm:inline">
            Dashboard
          </Link>
          <Link href="/properties" className="hidden text-slate-300 hover:text-white sm:inline">
            Properties
          </Link>
          <Link href="/buildings" className="hidden text-slate-300 hover:text-white sm:inline">
            Buildings
          </Link>
          <Link href="/login" className="inline-flex h-10 items-center gap-2 rounded-md bg-white px-4 font-semibold text-slate-950">
            Sign in
            <ArrowRight size={16} />
          </Link>
        </nav>
      </header>

      <section className="mx-auto grid min-h-[calc(100vh-4rem)] w-full max-w-7xl items-center gap-10 px-5 py-10 sm:px-8 lg:grid-cols-[1fr_440px]">
        <div className="max-w-3xl">
          <p className="text-sm font-semibold uppercase text-red-300">Fuzion Operations Platform</p>
          <h1 className="mt-4 text-4xl font-semibold tracking-normal text-white sm:text-5xl lg:text-6xl">
            Building Protection Passport&trade; & Digital Closeout
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-slate-300">
            A single front door for building registry, property readiness, closeout evidence, and Fuzion handover operations.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/login" className="inline-flex h-11 items-center gap-2 rounded-md bg-red-700 px-5 text-sm font-semibold text-white hover:bg-red-800">
              Go to login
              <ArrowRight size={16} />
            </Link>
            <Link href="/dashboard" className="inline-flex h-11 items-center rounded-md border border-white/20 px-5 text-sm font-semibold text-white hover:bg-white/10">
              Continue to dashboard
            </Link>
          </div>
        </div>

        <div className="rounded-lg border border-white/10 bg-white/5 p-5 shadow-2xl">
          <div className="flex items-center justify-between border-b border-white/10 pb-4">
            <div>
              <p className="text-sm font-semibold">Operations Snapshot</p>
              <p className="mt-1 text-xs text-slate-300">Placeholder access enabled for MVP review</p>
            </div>
            <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-200 ring-1 ring-emerald-400/30">
              Demo
            </span>
          </div>
          <div className="mt-5 grid gap-3">
            {platformSignals.map((signal) => {
              const Icon = signal.icon;
              return (
                <div key={signal.label} className="flex items-center justify-between rounded-md border border-white/10 bg-slate-900/80 p-4">
                  <div className="flex items-center gap-3">
                    <Icon size={18} className="text-red-300" />
                    <span className="text-sm font-medium">{signal.label}</span>
                  </div>
                  <span className="text-xs font-semibold text-slate-300">{signal.value}</span>
                </div>
              );
            })}
          </div>
        </div>
      </section>
    </main>
  );
}
