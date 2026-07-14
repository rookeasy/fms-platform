"use client";

import Image from "next/image";
import Link from "next/link";
import { ArrowLeft, Mail } from "lucide-react";

import { ProgressIndex } from "@/components/ProgressIndex";
import { fuzionBrand } from "@/lib/brand";

export default function PasswordResetPage() {
  return (
    <main className="fop-blueprint fop-fade-in flex min-h-screen items-center justify-center px-5 py-10 text-[color:var(--text-primary)]">
      <section className="w-full max-w-lg rounded-2xl border border-[color:var(--border)] bg-white p-6 shadow-[0_18px_44px_rgba(15,23,42,0.08)] sm:p-8">
        <Image src="/brand/fpp-logo.svg" alt={`${fuzionBrand.productName} logo`} width={250} height={74} priority className="h-auto w-[236px]" />
        <p className="mt-6 fop-label">Mission Control™ Access</p>
        <h1 className="mt-3 text-2xl font-semibold text-[color:var(--text-primary)]">Reset your FOP password</h1>
        <p className="mt-2 text-sm leading-6 text-[color:var(--text-secondary)]">
          Enter your email and the placeholder authentication flow will preserve the current MVP behavior.
        </p>
        <div className="mt-6">
          <ProgressIndex score={72} size="md" variant="dashboard" showScore={false} />
        </div>
        <form className="mt-6 space-y-4">
          <label className="block">
            <span className="text-sm font-medium text-[color:var(--text-secondary)]">Email</span>
            <span className="mt-2 flex h-12 items-center gap-3 rounded-xl border border-[color:var(--border)] bg-white px-3 text-[color:var(--text-primary)] focus-within:border-[color:var(--fop-build)]">
              <Mail size={18} className="text-[color:var(--text-muted)]" />
              <input name="email" type="email" autoComplete="email" placeholder="you@example.com" className="min-w-0 flex-1 border-0 bg-transparent text-sm outline-none" />
            </span>
          </label>
          <button type="submit" className="fop-button-primary h-12 w-full">
            Continue
          </button>
        </form>
        <div className="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-[color:var(--border)] pt-5 text-xs text-[color:var(--text-muted)]">
          <Link href="/login" className="inline-flex items-center gap-2 font-medium text-[color:var(--fop-build-text)] hover:text-[color:var(--text-primary)]">
            <ArrowLeft size={14} />
            Back to sign in
          </Link>
          <span>{fuzionBrand.version} · © {fuzionBrand.companyName}</span>
        </div>
      </section>
    </main>
  );
}
