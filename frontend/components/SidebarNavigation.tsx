"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ArrowDown,
  BadgeCheck,
  BarChart3,
  Building2,
  ClipboardCheck,
  Cpu,
  FileText,
  FolderKanban,
  Gauge,
  LayoutDashboard,
  LogIn,
  Map,
  Settings,
  ShieldCheck,
  Users,
  Wrench
} from "lucide-react";

import { FopLifecycleMark } from "@/components/brand/FopLifecycleMark";
import { fuzionBrand } from "@/lib/brand";
import { cn } from "@/lib/utils";

export const navigation = [
  { href: "/dashboard", label: "Mission Control", icon: LayoutDashboard },
  { href: "/buildings", label: "Buildings", icon: Building2 },
  { href: "/projects", label: "Projects", icon: FolderKanban },
  { href: "/properties", label: "Portfolios", icon: Map },
  { href: "/reports", label: "Estimating", icon: BarChart3 },
  { href: "/documents", label: "Engineering", icon: FileText },
  { href: "/closeout", label: "Construction", icon: Building2 },
  { href: "/work-orders", label: "Service", icon: Wrench },
  { href: "/inspections", label: "Inspections", icon: ClipboardCheck },
  { href: "/documents", label: "Building Library", icon: FileText },
  { href: "/certificates", label: "Finance", icon: BadgeCheck },
  { href: "/advisor", label: "Mission Briefing", icon: Cpu },
  { href: "/passports", label: "Building Passports", icon: ShieldCheck },
  { href: "/passports/onboarding", label: "Passport Queue", icon: ClipboardCheck },
  { href: "/deficiencies", label: "Deficiencies", icon: Gauge },
  { href: "/closeout", label: "Closeout", icon: ClipboardCheck },
  { href: "/users", label: "Administration", icon: Users },
  { href: "/memberships", label: "Memberships", icon: ShieldCheck },
  { href: "/settings", label: "Settings", icon: Settings },
  { href: "/login", label: "Login", icon: LogIn }
];

const navigationGroups = [
  { label: "Command", items: navigation.slice(0, 4) },
  { label: "Operating System", items: navigation.slice(4, 12) },
  { label: "Registry", items: navigation.slice(12) }
];

function ProductIdentity() {
  return (
    <div className="space-y-4">
      <FopLifecycleMark compact status="protect" className="h-[54px] w-[54px] shrink-0" title="FOP Living F mark" />
      <div>
        <p className="text-lg font-semibold text-[color:var(--text-primary)]">{fuzionBrand.product}</p>
        <p className="text-xs text-[color:var(--text-muted)]">{fuzionBrand.missionControlName}</p>
      </div>
      <div className="flex flex-wrap items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.18em]">
        <p style={{ color: "var(--fop-build)" }}>BUILD</p>
        <ArrowDown size={11} className="-rotate-90 text-[color:var(--text-muted)]" />
        <p style={{ color: "var(--fop-advise-text)" }}>ADVISE</p>
        <ArrowDown size={11} className="-rotate-90 text-[color:var(--text-muted)]" />
        <p style={{ color: "var(--fop-protect-text)" }}>PROTECT</p>
      </div>
      <p className="max-w-40 text-left text-[11px] font-medium leading-5 text-[color:var(--text-muted)]">
        {fuzionBrand.protectedMetric}
      </p>
    </div>
  );
}

export function SidebarNavigation() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-[17rem] shrink-0 border-r border-[color:var(--border)] bg-white text-[color:var(--text-primary)] lg:block">
      <div className="border-b border-[color:var(--border)] px-5 py-6">
        <ProductIdentity />
      </div>
      <nav className="flex flex-col gap-5 p-3">
        {navigationGroups.map((group) => (
          <div key={group.label}>
            <p className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-[0.22em] text-[color:var(--text-muted)]">{group.label}</p>
            <div className="space-y-1">
              {group.items.map((item) => {
                const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
                const Icon = item.icon;

                return (
                  <Link
                    key={`${item.href}-${item.label}`}
                    href={item.href}
                    className={cn(
                      "flex min-h-11 items-center gap-3 rounded-lg px-3 text-sm font-medium text-[color:var(--text-secondary)] transition duration-200",
                      isActive && "bg-[color:var(--fop-build-soft)] text-[color:var(--fop-build-text)] ring-1 ring-[color:var(--fop-build)]/25",
                      !isActive && "hover:bg-[color:var(--surface-elevated)] hover:text-[color:var(--text-primary)]"
                    )}
                  >
                    <Icon size={18} />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>
    </aside>
  );
}

export function MobileNavigation() {
  const pathname = usePathname();

  return (
    <nav className="border-b border-[color:var(--border)] bg-white px-4 py-3 lg:hidden" aria-label="Mobile navigation">
      <div className="flex gap-2 overflow-x-auto pb-1">
        {navigation.slice(0, 6).map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex min-h-10 shrink-0 items-center gap-2 rounded-xl border px-3 text-sm font-semibold transition duration-200",
                isActive
                  ? "border-[color:var(--fop-build)] bg-[color:var(--fop-build-soft)] text-[color:var(--fop-build-text)]"
                  : "border-[color:var(--border)] bg-[color:var(--surface)] text-[color:var(--text-secondary)] hover:border-[color:var(--fop-build)] hover:text-[color:var(--text-primary)]"
              )}
            >
              <Icon size={16} />
              {item.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
