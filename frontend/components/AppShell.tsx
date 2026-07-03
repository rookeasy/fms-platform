import type { ReactNode } from "react";

import { MobileNavigation, SidebarNavigation } from "@/components/SidebarNavigation";
import { TopBar } from "@/components/TopBar";

type AppShellProps = {
  title: string;
  children: ReactNode;
};

export function AppShell({ title, children }: AppShellProps) {
  return (
    <div className="fop-app-bg flex min-h-screen">
      <SidebarNavigation />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar title={title} />
        <MobileNavigation />
        <main className="fop-page mx-auto w-full max-w-[1600px] flex-1 px-4 py-6 sm:px-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}
