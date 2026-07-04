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
    <main className="fop-blueprint fop-fade-in flex min-h-screen items-center justify-center bg-[#050A18] px-5 py-10 text-white">
      <section className="w-full max-w-md rounded-3xl border border-white/12 bg-white/[0.08] p-6 shadow-[0_24px_80px_rgba(0,0,0,0.45)] backdrop-blur-xl sm:p-8">
        <div className="text-center">
          <Image src="/brand/fpp-logo.svg" alt={`${fuzionBrand.productName} logo`} width={230} height={62} priority className="mx-auto" />
          <h1 className="mt-6 text-2xl font-semibold text-white">Sign in to FPP</h1>
          <p className="mt-2 text-sm leading-6 text-slate-300">{fuzionBrand.contractorSubtitle}</p>
        </div>
        <div className="mt-6">
          <ProgressIndex score={86} size="md" variant="dashboard" showScore={false} />
        </div>
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <label className="block">
            <span className="text-sm font-medium text-slate-200">Email</span>
            <span className="mt-2 flex h-12 items-center gap-3 rounded-xl border border-white/12 bg-[#050A18]/60 px-3 text-slate-100 focus-within:border-[#FF6B5F]/70">
              <Mail size={18} className="text-[#7D8CA3]" />
              <input name="email" type="email" autoComplete="email" defaultValue="demo@fpp.local" className="min-w-0 flex-1 border-0 bg-transparent text-sm outline-none" />
            </span>
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-200">Password</span>
            <span className="mt-2 flex h-12 items-center gap-3 rounded-xl border border-white/12 bg-[#050A18]/60 px-3 text-slate-100 focus-within:border-[#FF6B5F]/70">
              <LockKeyhole size={18} className="text-[#7D8CA3]" />
              <input name="password" type="password" autoComplete="current-password" defaultValue="password" className="min-w-0 flex-1 border-0 bg-transparent text-sm outline-none" />
            </span>
          </label>
          <button type="submit" className="flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-[#FF6B5F] text-sm font-semibold text-[#050A18]">
            Sign In
            <ArrowRight size={16} />
          </button>
        </form>
        <div className="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-white/10 pt-5 text-xs text-slate-400">
          <Link href="/password-reset" className="font-medium text-[#FFB4AD] hover:text-white">Forgot password?</Link>
          <span>{fuzionBrand.version} · © {fuzionBrand.companyName}</span>
        </div>
      </section>
    </main>
  );
}
