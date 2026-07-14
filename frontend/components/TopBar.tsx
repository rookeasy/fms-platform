import { Bell, UserCircle } from "lucide-react";

import { GlobalSearch } from "@/components/GlobalSearch";

type TopBarProps = {
  title: string;
};

export function TopBar({ title }: TopBarProps) {
  return (
    <header className="sticky top-0 z-40 flex min-h-20 flex-wrap items-center justify-between gap-4 border-b border-[color:var(--border)] bg-white px-6 py-3">
      <div className="min-w-0">
        <p className="fop-label">Mission Control™</p>
        <h1 className="min-w-0 text-2xl font-semibold tracking-normal text-[color:var(--text-primary)]">{title}</h1>
      </div>
      <div className="flex min-w-0 flex-1 items-center justify-end gap-2">
        <GlobalSearch />
        <button
          type="button"
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-[color:var(--border)] bg-white text-[color:var(--text-secondary)] transition hover:border-[color:var(--fop-build)] hover:text-[color:var(--text-primary)]"
          aria-label="Notifications"
          title="Notifications"
        >
          <Bell size={18} />
        </button>
        <button
          type="button"
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-[color:var(--border)] bg-white text-[color:var(--text-secondary)] transition hover:border-[color:var(--fop-build)] hover:text-[color:var(--text-primary)]"
          aria-label="User menu"
          title="User menu"
        >
          <UserCircle size={20} />
        </button>
      </div>
    </header>
  );
}
