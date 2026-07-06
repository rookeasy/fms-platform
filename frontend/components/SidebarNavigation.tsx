"use client";

import Image from "next/image";
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

import { cn } from "@/lib/utils";
import { fuzionBrand } from "@/lib/brand";

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
  { href: "/documents", label: "Documents", icon: FileText },
  { href: "/certificates", label: "Finance", icon: BadgeCheck },
  { href: "/advisor", label: "Mission Briefing", icon: Cpu },
  { href: "/passports", label: "Building Passports", icon: ShieldCheck },
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
    <div className="flex items-start gap-3">
      <Image src="/brand/fpp-mark.svg" alt="" width={34} height={34} />
      <div>
        <p className="text-lg font-semibold text-white">{fuzionBrand.shortName}</p>
        <p className="text-xs text-slate-300">{fuzionBrand.productName}</p>
        <div className="mt-4 space-y-1 text-[10px] font-semibold uppercase tracking-[0.2em]">
          <p className="text-slate-300">BUILD</p>
          <ArrowDown size={12} className="text-slate-500" />
          <p className="text-[#93B7F8]">ADVISE</p>
          <ArrowDown size={12} className="text-slate-500" />
          <p className="text-[#E9A099]">PROTECT</p>
        </div>
        <p className="mt-5 max-w-36 text-left text-[11px] font-medium leading-5 text-slate-400">
          Projects end.
          <br />
          Buildings remain.
        </p>
      </div>
    </div>
  );
}

export function SidebarNavigation() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-[17rem] shrink-0 border-r border-[#1E293B] bg-[#0F172A] text-white shadow-[10px_0_28px_rgba(15,23,42,0.16)] lg:block">
      <div className="border-b border-white/10 px-5 py-6">
        <ProductIdentity />
      </div>
      <nav className="flex flex-col gap-5 p-3">
        {navigationGroups.map((group) => (
          <div key={group.label}>
            <p className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500">{group.label}</p>
            <div className="space-y-1">
              {group.items.map((item) => {
                const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
                const Icon = item.icon;

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "flex min-h-11 items-center gap-3 rounded-xl px-3 text-sm font-medium text-slate-300 transition duration-200",
                      isActive && "bg-[#D95A4E] text-white shadow-[0_10px_24px_rgba(217,90,78,0.20)]",
                      !isActive && "hover:bg-white/10 hover:text-white"
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
    <nav className="border-b border-[#E2E8F0] bg-white/92 px-4 py-3 shadow-lg backdrop-blur-xl lg:hidden" aria-label="Mobile navigation">
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
                  ? "border-[#D95A4E] bg-[#D95A4E] text-white"
                  : "border-[#E2E8F0] bg-white text-[#475569] hover:border-[#D95A4E]/35 hover:text-[#0F172A]"
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
