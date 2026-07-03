"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight, LockKeyhole, Mail, ShieldCheck } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    router.push("/dashboard");
  }

  return (
    <main className="grid min-h-screen bg-slate-100 lg:grid-cols-[1fr_480px]">
      <section className="flex min-h-[42vh] flex-col justify-between bg-slate-950 px-6 py-8 text-white sm:px-10 lg:min-h-screen">
        <Link href="/" className="flex w-fit items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-md bg-red-700 text-sm font-semibold">F</span>
          <span>
            <span className="block text-sm font-semibold">FOP</span>
            <span className="block text-xs text-slate-300">Fuzion Operations Platform</span>
          </span>
        </Link>

        <div className="max-w-2xl py-12">
          <p className="text-sm font-semibold uppercase text-red-300">Fuzion Operations Platform</p>
          <h1 className="mt-4 text-4xl font-semibold tracking-normal sm:text-5xl">
            Building Protection Passport&trade; & Digital Closeout.
          </h1>
          <p className="mt-5 text-base leading-7 text-slate-300">
            Access building profiles, property readiness, closeout scoring, and Fuzion handover operations from one workspace.
          </p>
        </div>

        <div className="grid gap-3 text-sm text-slate-300 sm:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3">
          {["Registry", "Closeout", "Readiness"].map((item) => (
            <div key={item} className="rounded-md border border-white/10 bg-white/5 p-3">
              <p className="font-semibold text-white">{item}</p>
              <p className="mt-1 text-xs">MVP access enabled</p>
            </div>
          ))}
        </div>
      </section>

      <section className="flex items-center justify-center px-6 py-10">
        <div className="w-full max-w-md rounded-lg border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm font-semibold uppercase text-slate-500">Sign in</p>
              <h2 className="mt-2 text-2xl font-semibold text-slate-950">Fuzion Operations Platform</h2>
            </div>
            <ShieldCheck className="text-red-700" size={24} />
          </div>

          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            <label className="block">
              <span className="text-sm font-medium text-slate-700">Email</span>
              <span className="mt-2 flex h-11 items-center gap-2 rounded-md border border-slate-300 px-3">
                <Mail size={17} className="text-slate-400" />
                <input
                  name="email"
                  type="email"
                  autoComplete="email"
                  defaultValue="demo@fop.local"
                  className="min-w-0 flex-1 border-0 bg-transparent text-sm outline-none"
                />
              </span>
            </label>

            <label className="block">
              <span className="text-sm font-medium text-slate-700">Password</span>
              <span className="mt-2 flex h-11 items-center gap-2 rounded-md border border-slate-300 px-3">
                <LockKeyhole size={17} className="text-slate-400" />
                <input
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  defaultValue="password"
                  className="min-w-0 flex-1 border-0 bg-transparent text-sm outline-none"
                />
              </span>
            </label>

            <button
              type="submit"
              className="flex h-11 w-full items-center justify-center gap-2 rounded-md bg-red-700 text-sm font-semibold text-white hover:bg-red-800"
            >
              Sign in
              <ArrowRight size={16} />
            </button>

            <Link
              href="/dashboard"
              className="flex h-11 w-full items-center justify-center rounded-md border border-slate-300 text-sm font-semibold text-slate-800 hover:bg-slate-50"
            >
              Continue to dashboard
            </Link>
          </form>

          <p className="mt-5 rounded-md bg-amber-50 px-3 py-2 text-xs leading-5 text-amber-900 ring-1 ring-amber-200">
            MVP note: authentication is placeholder-only in this environment.
          </p>
        </div>
      </section>
    </main>
  );
}
