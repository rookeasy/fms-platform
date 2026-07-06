import { Bell, UserCircle } from "lucide-react";

import { GlobalSearch } from "@/components/GlobalSearch";

type TopBarProps = {
  title: string;
};

export function TopBar({ title }: TopBarProps) {
  return (
    <header className="sticky top-0 z-40 flex min-h-20 flex-wrap items-center justify-between gap-4 border-b border-[#E2E8F0] bg-white/92 px-6 py-3 shadow-[0_10px_32px_rgba(15,23,42,0.06)] backdrop-blur-xl">
      <h1 className="min-w-0 text-2xl font-semibold tracking-normal text-[#0F172A]">{title}</h1>
      <div className="flex min-w-0 flex-1 items-center justify-end gap-2">
        <GlobalSearch />
        <button
          type="button"
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-[#E2E8F0] bg-white text-[#64748B] transition hover:border-[#D95A4E]/35 hover:text-[#0F172A]"
          aria-label="Notifications"
          title="Notifications"
        >
          <Bell size={18} />
        </button>
        <button
          type="button"
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-[#E2E8F0] bg-white text-[#64748B] transition hover:border-[#D95A4E]/35 hover:text-[#0F172A]"
          aria-label="User menu"
          title="User menu"
        >
          <UserCircle size={20} />
        </button>
      </div>
    </header>
  );
}
