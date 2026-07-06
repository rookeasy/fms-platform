"use client";

import Image from "next/image";
import Link from "next/link";
import { ArrowLeft, Mail } from "lucide-react";

import { ProgressIndex } from "@/components/ProgressIndex";
import { fuzionBrand } from "@/lib/brand";

export default function PasswordResetPage() {
  return (
    <main className="fop-blueprint fop-fade-in flex min-h-screen items-center justify-center bg-[#0F172A] px-5 py-10 text-white">
      <section className="w-full max-w-lg rounded-3xl border border-white/12 bg-white/[0.08] p-6 shadow-[0_24px_64px_rgba(2,6,23,0.34)] backdrop-blur-xl sm:p-8">
        <Image src="/brand/fpp-logo.svg" alt={`${fuzionBrand.productName} logo`} width={236} height={64} priority />
        <p className="mt-6 text-xs font-semibold uppercase tracking-[0.24em] text-[#E9A099]">Account Access</p>
        <h1 className="mt-3 text-2xl font-semibold text-white">Reset your FOP password</h1>
        <p className="mt-2 text-sm leading-6 text-slate-300">
          Enter your email and the placeholder authentication flow will preserve the current MVP behavior.
        </p>
        <div className="mt-6">
          <ProgressIndex score={72} size="md" variant="dashboard" showScore={false} />
        </div>
        <form className="mt-6 space-y-4">
          <label className="block">
            <span className="text-sm font-medium text-slate-200">Email</span>
            <span className="mt-2 flex h-12 items-center gap-3 rounded-xl border border-white/12 bg-[#111827]/60 px-3 text-slate-100 focus-within:border-[#D95A4E]/70">
              <Mail size={18} className="text-[#7D8CA3]" />
              <input name="email" type="email" autoComplete="email" placeholder="you@example.com" className="min-w-0 flex-1 border-0 bg-transparent text-sm outline-none" />
            </span>
          </label>
          <button type="submit" className="h-12 w-full rounded-xl bg-[#D95A4E] text-sm font-semibold text-white">
            Continue
          </button>
        </form>
        <div className="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-white/10 pt-5 text-xs text-slate-400">
          <Link href="/login" className="inline-flex items-center gap-2 font-medium text-[#E9A099] hover:text-white">
            <ArrowLeft size={14} />
            Back to sign in
          </Link>
          <span>{fuzionBrand.version} · © {fuzionBrand.companyName}</span>
        </div>
      </section>
    </main>
  );
}
