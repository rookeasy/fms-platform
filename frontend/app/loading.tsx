import Image from "next/image";

import { fuzionBrand } from "@/lib/brand";

export default function Loading() {
  return (
    <main className="fop-blueprint flex min-h-screen items-center justify-center px-6 text-[color:var(--text-primary)]">
      <div className="text-center">
        <Image
          src="/brand/fpp-logo.svg"
          alt={`${fuzionBrand.productName} logo`}
          width={260}
          height={76}
          priority
          className="mx-auto h-auto w-[240px]"
        />
        <p className="mt-5 text-sm font-semibold uppercase tracking-[0.26em] text-[color:var(--fop-build-text)]">
          {fuzionBrand.missionControlName}
        </p>
        <p className="mt-2 text-xs font-semibold text-[color:var(--text-muted)]">{fuzionBrand.tagline}</p>
      </div>
    </main>
  );
}
