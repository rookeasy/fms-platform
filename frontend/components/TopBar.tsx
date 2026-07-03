import Link from "next/link";
import { Bell, Cpu, ShieldCheck, UserCircle } from "lucide-react";

import { GlobalSearch } from "@/components/GlobalSearch";
import { fuzionBrand } from "@/lib/brand";

type TopBarProps = {
  title: string;
};

export function TopBar({ title }: TopBarProps) {
  return (
    <header className="sticky top-0 z-40 flex min-h-20 flex-wrap items-center justify-between gap-4 border-b border-white/10 bg-[#0B1224]/90 px-6 py-3 shadow-[0_14px_40px_rgba(0,0,0,0.22)] backdrop-blur-xl">
      <div className="min-w-0">
        <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-[#7D8CA3]">{fuzionBrand.productName}</p>
        <h1 className="mt-1 text-2xl font-semibold tracking-normal text-white">{title}</h1>
      </div>
      <div className="flex min-w-0 flex-1 items-center justify-end gap-2">
        <GlobalSearch />
        <Link href="/advisor" className="fop-button-primary hidden h-10 min-h-10 xl:inline-flex">
          <Cpu size={16} />
          Ask Fuzion
        </Link>
        <div className="hidden min-h-10 items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 text-xs font-semibold uppercase tracking-[0.18em] text-[#B6C1CF] 2xl:flex">
          <ShieldCheck size={16} className="text-[#FF6B5F]" />
          {fuzionBrand.tagline}
        </div>
        <button
          type="button"
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-[#B6C1CF] transition hover:border-white/20 hover:text-white"
          aria-label="Notifications"
          title="Notifications"
        >
          <Bell size={18} />
        </button>
        <button
          type="button"
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-[#B6C1CF] transition hover:border-white/20 hover:text-white"
          aria-label="User menu"
          title="User menu"
        >
          <UserCircle size={20} />
        </button>
      </div>
    </header>
  );
}

