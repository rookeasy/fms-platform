import { Bell, UserCircle } from "lucide-react";

import { GlobalSearch } from "@/components/GlobalSearch";

type TopBarProps = {
  title: string;
};

export function TopBar({ title }: TopBarProps) {
  return (
    <header className="flex min-h-16 flex-wrap items-center justify-between gap-4 border-b border-slate-200 bg-white px-6 py-3">
      <div className="min-w-0">
        <p className="text-xs font-semibold uppercase text-slate-500">Fuzion Operations Platform</p>
        <h1 className="text-xl font-semibold text-slate-950">{title}</h1>
      </div>
      <div className="flex min-w-0 flex-1 items-center justify-end gap-2">
        <GlobalSearch />
        <button
          type="button"
          className="flex h-10 w-10 items-center justify-center rounded-md border border-slate-200 text-slate-600"
          aria-label="Notifications"
          title="Notifications"
        >
          <Bell size={18} />
        </button>
        <button
          type="button"
          className="flex h-10 w-10 items-center justify-center rounded-md border border-slate-200 text-slate-600"
          aria-label="User menu"
          title="User menu"
        >
          <UserCircle size={20} />
        </button>
      </div>
    </header>
  );
}
