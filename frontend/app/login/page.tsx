"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight, LockKeyhole, Mail } from "lucide-react";

import { ProgressIndex } from "@/components/ProgressIndex";
import { fuzionBrand } from "@/lib/brand";

export default function LoginPage() {
  const router = useRouter();

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    router.push("/dashboard");
  }

  return (
    <main className="fop-blueprint fop-fade-in grid min-h-screen overflow-hidden bg-[#0F172A] text-white lg:grid-cols-[minmax(0,1fr)_520px]">
      <section className="relative flex min-h-[52vh] flex-col justify-between px-5 py-6 sm:px-10 lg:min-h-screen lg:px-14 lg:py-10">
        <div className="pointer-events-none absolute right-8 top-16 hidden h-72 w-72 rounded-full border border-white/8 lg:block" />
        <div className="pointer-events-none absolute bottom-28 right-36 hidden h-px w-44 rotate-[-18deg] bg-gradient-to-r from-[#D95A4E]/38 to-transparent lg:block" />

        <Link href="/" className="relative flex w-fit items-center gap-3">
          <Image src="/brand/fpp-mark.svg" alt={`${fuzionBrand.productName} logo`} width={44} height={44} priority />
          <span>
            <span className="block text-sm font-semibold tracking-[0.18em]">{fuzionBrand.shortName}</span>
            <span className="block text-xs text-slate-400">{fuzionBrand.companyName}</span>
          </span>
        </Link>

        <div className="relative max-w-3xl py-12 lg:py-16">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-[#E9A099]">Fuzion Operating Platform</p>
          <h1 className="mt-5 max-w-3xl text-4xl font-semibold leading-tight tracking-normal text-white sm:text-5xl xl:text-6xl">
            {fuzionBrand.subtitle}
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-slate-300">
            The building protection platform for owners, contractors, and property teams.
          </p>
          <p className="mt-5 text-sm font-semibold tracking-[0.22em] text-[#E9A099]">{fuzionBrand.protectedMetric}</p>
        </div>

        <div className="relative grid gap-3 sm:grid-cols-3">
          {fuzionBrand.brandPromise.map((item) => (
            <div key={item.label} className="rounded-xl border border-white/10 bg-white/[0.045] p-4 shadow-2xl backdrop-blur">
              <p className="text-sm font-semibold tracking-[0.2em] text-[#E9A099]">{item.label}</p>
              <p className="mt-2 text-sm text-slate-300">{item.description}</p>
            </div>
          ))}
        </div>
        <div className="relative mt-5">
          <ProgressIndex score={86} size="md" variant="dashboard" showDescriptions showScore={false} />
        </div>
      </section>

      <section className="relative flex items-center justify-center px-5 py-8 sm:px-8 lg:min-h-screen lg:py-10">
        <div className="w-full max-w-md rounded-3xl border border-white/12 bg-white/[0.08] p-6 shadow-[0_24px_64px_rgba(2,6,23,0.34)] backdrop-blur-xl sm:p-8">
          <div className="text-center">
            <div className="fop-logo-fade relative mx-auto h-[61px] w-[228px]">
              <Image src="/brand/fpp-logo.svg" alt={`${fuzionBrand.productName} logo`} width={228} height={61} priority />
              <span className="fop-mark-pulse pointer-events-none absolute left-6 top-5 h-5 w-5 rounded-full border border-[#E9A099]/75" />
            </div>
            <h2 className="mt-6 text-2xl font-semibold text-white">Sign in to FOP</h2>
            <p className="mt-2 text-sm text-slate-300">{fuzionBrand.contractorSubtitle}</p>
          </div>

          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <label className="block">
              <span className="text-sm font-medium text-slate-200">Email</span>
              <span className="mt-2 flex h-12 items-center gap-3 rounded-xl border border-white/12 bg-[#111827]/60 px-3 text-slate-100 ring-1 ring-transparent transition focus-within:border-[#D95A4E]/70 focus-within:ring-[#D95A4E]/20">
                <Mail size={18} className="text-[#7D8CA3]" />
                <input name="email" type="email" autoComplete="email" defaultValue="demo@fop.local" className="min-w-0 flex-1 border-0 bg-transparent text-sm outline-none placeholder:text-[#B6C1CF]" />
              </span>
            </label>

            <label className="block">
              <span className="text-sm font-medium text-slate-200">Password</span>
              <span className="mt-2 flex h-12 items-center gap-3 rounded-xl border border-white/12 bg-[#111827]/60 px-3 text-slate-100 ring-1 ring-transparent transition focus-within:border-[#D95A4E]/70 focus-within:ring-[#D95A4E]/20">
                <LockKeyhole size={18} className="text-[#7D8CA3]" />
                <input name="password" type="password" autoComplete="current-password" defaultValue="password" className="min-w-0 flex-1 border-0 bg-transparent text-sm outline-none placeholder:text-[#B6C1CF]" />
              </span>
            </label>

            <div className="flex flex-wrap items-center justify-between gap-3 text-sm">
              <label className="flex items-center gap-2 text-slate-300">
                <input type="checkbox" className="h-4 w-4 rounded border-white/20 bg-[#111827] accent-[#D95A4E]" />
                Remember me
              </label>
              <Link href="/password-reset" className="font-medium text-[#E9A099] hover:text-white">
                Forgot password?
              </Link>
            </div>

            <button type="submit" className="flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-[#D95A4E] text-sm font-semibold text-white shadow-[0_14px_30px_rgba(217,90,78,0.20)] transition hover:bg-[#C94F44]">
              Sign In
              <ArrowRight size={16} />
            </button>
          </form>

          <div className="mt-8 flex flex-wrap items-center justify-between gap-3 border-t border-white/10 pt-5 text-xs text-slate-400">
            <span>{fuzionBrand.version}</span>
            <span>© {fuzionBrand.companyName}</span>
          </div>
        </div>
      </section>
    </main>
  );
}
