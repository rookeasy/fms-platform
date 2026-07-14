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
    <main className="fop-blueprint fop-fade-in grid min-h-screen overflow-hidden text-[color:var(--text-primary)] lg:grid-cols-[minmax(0,1fr)_500px]">
      <section className="flex min-h-[52vh] flex-col justify-between px-5 py-6 sm:px-10 lg:min-h-screen lg:px-14 lg:py-10">
        <Link href="/" className="block w-fit">
          <Image src="/brand/fpp-logo.svg" alt={`${fuzionBrand.productName} logo`} width={356} height={104} priority className="h-auto w-[260px]" />
        </Link>

        <div className="max-w-3xl py-12 lg:py-16">
          <p className="fop-label">{fuzionBrand.product}</p>
          <h1 className="mt-5 max-w-3xl text-4xl font-semibold leading-tight tracking-normal text-[color:var(--text-primary)] sm:text-5xl xl:text-6xl">
            {fuzionBrand.missionControlSubtitle}
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-[color:var(--text-secondary)]">
            Buildings Under Protection™ begins with clear records, confident handover, and disciplined lifecycle intelligence.
          </p>
          <p className="mt-5 text-sm font-semibold tracking-[0.22em] text-[color:var(--fop-build-text)]">{fuzionBrand.tagline}</p>
        </div>

        <div className="grid gap-3 sm:grid-cols-3">
          {fuzionBrand.brandPromise.map((item) => (
            <div key={item.label} className="rounded-lg border border-[color:var(--border)] bg-white p-4 shadow-sm">
              <p className="text-sm font-semibold tracking-[0.2em] text-[color:var(--fop-build-text)]">{item.label}</p>
              <p className="mt-2 text-sm text-[color:var(--text-secondary)]">{item.description}</p>
            </div>
          ))}
        </div>
        <div className="mt-5 max-w-2xl">
          <ProgressIndex score={86} size="md" variant="dashboard" showDescriptions showScore={false} />
        </div>
      </section>

      <section className="flex items-center justify-center bg-white px-5 py-8 shadow-[0_0_60px_rgba(15,23,42,0.08)] sm:px-8 lg:min-h-screen lg:py-10">
        <div className="w-full max-w-md rounded-2xl border border-[color:var(--border)] bg-white p-6 shadow-[0_18px_44px_rgba(15,23,42,0.08)] sm:p-8">
          <div className="text-center">
            <Image src="/brand/fpp-logo.svg" alt={`${fuzionBrand.productName} logo`} width={260} height={76} priority className="mx-auto h-auto w-[240px]" />
            <h2 className="mt-6 text-2xl font-semibold text-[color:var(--text-primary)]">Sign in to FOP</h2>
            <p className="mt-2 text-sm text-[color:var(--text-secondary)]">{fuzionBrand.contractorSubtitle}</p>
          </div>

          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <label className="block">
              <span className="text-sm font-medium text-[color:var(--text-secondary)]">Email</span>
              <span className="mt-2 flex h-12 items-center gap-3 rounded-xl border border-[color:var(--border)] bg-white px-3 text-[color:var(--text-primary)] ring-1 ring-transparent transition focus-within:border-[color:var(--fop-build)] focus-within:ring-[color:var(--fop-build)]/20">
                <Mail size={18} className="text-[color:var(--text-muted)]" />
                <input name="email" type="email" autoComplete="email" defaultValue="demo@fop.local" className="min-w-0 flex-1 border-0 bg-transparent text-sm outline-none placeholder:text-[color:var(--text-muted)]" />
              </span>
            </label>

            <label className="block">
              <span className="text-sm font-medium text-[color:var(--text-secondary)]">Password</span>
              <span className="mt-2 flex h-12 items-center gap-3 rounded-xl border border-[color:var(--border)] bg-white px-3 text-[color:var(--text-primary)] ring-1 ring-transparent transition focus-within:border-[color:var(--fop-build)] focus-within:ring-[color:var(--fop-build)]/20">
                <LockKeyhole size={18} className="text-[color:var(--text-muted)]" />
                <input name="password" type="password" autoComplete="current-password" defaultValue="password" className="min-w-0 flex-1 border-0 bg-transparent text-sm outline-none placeholder:text-[color:var(--text-muted)]" />
              </span>
            </label>

            <div className="flex flex-wrap items-center justify-between gap-3 text-sm">
              <label className="flex items-center gap-2 text-[color:var(--text-secondary)]">
                <input type="checkbox" className="h-4 w-4 rounded border-[color:var(--border)] accent-[color:var(--fop-build)]" />
                Remember me
              </label>
              <Link href="/password-reset" className="font-medium text-[color:var(--fop-build-text)] hover:text-[color:var(--text-primary)]">
                Forgot password?
              </Link>
            </div>

            <button type="submit" className="fop-button-primary h-12 w-full">
              Sign In
              <ArrowRight size={16} />
            </button>
          </form>

          <div className="mt-8 flex flex-wrap items-center justify-between gap-3 border-t border-[color:var(--border)] pt-5 text-xs text-[color:var(--text-muted)]">
            <span>{fuzionBrand.version}</span>
            <span>© {fuzionBrand.companyName}</span>
          </div>
        </div>
      </section>
    </main>
  );
}
