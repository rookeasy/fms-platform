import Link from "next/link";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-100 px-6">
      <section className="w-full max-w-md rounded-lg border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase text-slate-500">FMS Platform</p>
        <h1 className="mt-3 text-3xl font-semibold text-slate-950">Sign in</h1>
        <div className="mt-8 space-y-4">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Email</span>
            <input className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3" defaultValue="demo@fms.local" />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Password</span>
            <input className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3" type="password" defaultValue="password" />
          </label>
          <Link
            href="/dashboard"
            className="flex h-11 w-full items-center justify-center rounded-md bg-slate-950 text-sm font-semibold text-white"
          >
            Sign in
          </Link>
        </div>
      </section>
    </main>
  );
}
