"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight, LockKeyhole, Mail } from "lucide-react";

import { ProgressIndex } from "@/components/ProgressIndex";
import { fuzionBrand } from "@/lib/brand";

export default function MinimalLoginPage() {
  const router = useRouter();

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    router.push("/dashboard");
  }

  return (
    <main className="fop-blueprint fop-fade-in flex min-h-screen items-center justify-center px-5 py-10 text-[color:var(--text-primary)]">
      <section className="w-full max-w-md rounded-2xl border border-[color:var(--border)] bg-white p-6 shadow-[0_18px_44px_rgba(15,23,42,0.08)] sm:p-8">
        <div className="text-center">
          <Image src="/brand/fpp-logo.svg" alt={`${fuzionBrand.productName} logo`} width={250} height={74} priority className="mx-auto h-auto w-[230px]" />
          <h1 className="mt-6 text-2xl font-semibold text-[color:var(--text-primary)]">Sign in to Fuzion</h1>
          <p className="mt-2 text-sm leading-6 text-[color:var(--text-secondary)]">{fuzionBrand.contractorSubtitle}</p>
          <p className="mt-2 text-xs font-semibold tracking-[0.18em] text-[color:var(--fop-build-text)]">{fuzionBrand.protectedMetric}</p>
        </div>
        <div className="mt-6">
          <ProgressIndex score={86} size="md" variant="dashboard" showScore={false} />
        </div>
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <label className="block">
            <span className="text-sm font-medium text-[color:var(--text-secondary)]">Email</span>
            <span className="mt-2 flex h-12 items-center gap-3 rounded-xl border border-[color:var(--border)] bg-white px-3 text-[color:var(--text-primary)] focus-within:border-[color:var(--fop-build)]">
              <Mail size={18} className="text-[color:var(--text-muted)]" />
              <input name="email" type="email" autoComplete="email" defaultValue="demo@fop.local" className="min-w-0 flex-1 border-0 bg-transparent text-sm outline-none" />
            </span>
          </label>
          <label className="block">
            <span className="text-sm font-medium text-[color:var(--text-secondary)]">Password</span>
            <span className="mt-2 flex h-12 items-center gap-3 rounded-xl border border-[color:var(--border)] bg-white px-3 text-[color:var(--text-primary)] focus-within:border-[color:var(--fop-build)]">
              <LockKeyhole size={18} className="text-[color:var(--text-muted)]" />
              <input name="password" type="password" autoComplete="current-password" defaultValue="password" className="min-w-0 flex-1 border-0 bg-transparent text-sm outline-none" />
            </span>
          </label>
          <button type="submit" className="fop-button-primary h-12 w-full">
            Sign In
            <ArrowRight size={16} />
          </button>
        </form>
        <div className="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-[color:var(--border)] pt-5 text-xs text-[color:var(--text-muted)]">
          <Link href="/password-reset" className="font-medium text-[color:var(--fop-build-text)] hover:text-[color:var(--text-primary)]">Forgot password?</Link>
          <span>{fuzionBrand.version} · © {fuzionBrand.companyName}</span>
        </div>
      </section>
    </main>
  );
}
