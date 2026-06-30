import type { ReactNode } from "react";

import { SidebarNavigation } from "@/components/SidebarNavigation";
import { TopBar } from "@/components/TopBar";

type AppShellProps = {
  title: string;
  children: ReactNode;
};

export function AppShell({ title, children }: AppShellProps) {
  return (
    <div className="flex min-h-screen bg-slate-100">
      <SidebarNavigation />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar title={title} />
        <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}
