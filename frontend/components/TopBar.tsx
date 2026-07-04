import { Bell, UserCircle } from "lucide-react";

import { GlobalSearch } from "@/components/GlobalSearch";

type TopBarProps = {
  title: string;
};

export function TopBar({ title }: TopBarProps) {
  return (
    <header className="sticky top-0 z-40 flex min-h-20 flex-wrap items-center justify-between gap-4 border-b border-white/10 bg-[#0B1224]/90 px-6 py-3 shadow-[0_14px_40px_rgba(0,0,0,0.22)] backdrop-blur-xl">
      <h1 className="min-w-0 text-2xl font-semibold tracking-normal text-white">{title}</h1>
      <div className="flex min-w-0 flex-1 items-center justify-end gap-2">
        <GlobalSearch />
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
