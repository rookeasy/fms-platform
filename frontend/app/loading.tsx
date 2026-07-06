import Image from "next/image";

import { fuzionBrand } from "@/lib/brand";

export default function Loading() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[#0F172A] px-6 text-white">
      <div className="text-center">
        <Image
          src="/brand/fpp-logo.svg"
          alt={`${fuzionBrand.productName} logo`}
          width={240}
          height={64}
          priority
          className="mx-auto"
        />
        <p className="mt-5 text-sm font-semibold uppercase tracking-[0.26em] text-slate-300">
          {fuzionBrand.productName}
        </p>
        <p className="mt-2 text-xs font-semibold text-[#E9A099]">{fuzionBrand.tagline}</p>
      </div>
    </main>
  );
}

