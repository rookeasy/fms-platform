"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BadgeCheck,
  BarChart3,
  Building2,
  ClipboardCheck,
  Cpu,
  Map,
  FileText,
  Gauge,
  LogIn,
  LayoutDashboard,
  Settings,
  ShieldCheck,
  Users,
  Wrench
} from "lucide-react";

import { cn } from "@/lib/utils";
import { fuzionBrand } from "@/lib/brand";

export const navigation = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/properties", label: "Projects", icon: Map },
  { href: "/reports", label: "Estimating", icon: BarChart3 },
  { href: "/documents", label: "Engineering", icon: FileText },
  { href: "/buildings", label: "Construction", icon: Building2 },
  { href: "/work-orders", label: "Service", icon: Wrench },
  { href: "/inspections", label: "Inspections", icon: ClipboardCheck },
  { href: "/certificates", label: "Finance", icon: BadgeCheck },
  { href: "/advisor", label: "AI / Advisor", icon: Cpu },
  { href: "/users", label: "Administration", icon: Users },
  { href: "/deficiencies", label: "Deficiencies", icon: Gauge },
  { href: "/memberships", label: "Memberships", icon: ShieldCheck },
  { href: "/settings", label: "Settings", icon: Settings },
  { href: "/login", label: "Login", icon: LogIn }
];

const navigationGroups = [
  { label: "Command", items: navigation.slice(0, 2) },
  { label: "Operating System", items: navigation.slice(2, 9) },
  { label: "Control", items: navigation.slice(9) }
];

export function SidebarNavigation() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-72 shrink-0 border-r border-white/10 bg-[#050A18] text-white shadow-2xl lg:block">
      <div className="flex h-20 items-center border-b border-white/10 px-5">
        <div className="flex items-center gap-3">
          <Image src="/brand/fuzion-tech-mark.svg" alt="" width={34} height={34} />
          <div>
            <p className="text-lg font-semibold text-white">{fuzionBrand.shortName}</p>
            <p className="text-xs text-[#B6C1CF]">{fuzionBrand.productName}</p>
          </div>
        </div>
      </div>
      <div className="border-b border-white/10 px-5 py-4">
        <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-[#FFB4AD]">{fuzionBrand.tagline}</p>
      </div>
      <nav className="flex flex-col gap-5 p-3">
        {navigationGroups.map((group) => (
          <div key={group.label}>
            <p className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-[0.22em] text-[#7D8CA3]">{group.label}</p>
            <div className="space-y-1">
              {group.items.map((item) => {
                const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
                const Icon = item.icon;

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "flex min-h-11 items-center gap-3 rounded-xl px-3 text-sm font-medium text-[#B6C1CF] transition duration-200",
                      isActive && "bg-[#FF6B5F] text-[#050A18] shadow-lg",
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
    <nav className="border-b border-white/10 bg-[#0B1224]/92 px-4 py-3 shadow-lg backdrop-blur-xl lg:hidden" aria-label="Mobile navigation">
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
                  ? "border-[#FF6B5F] bg-[#FF6B5F] text-[#050A18]"
                  : "border-white/10 bg-white/5 text-[#B6C1CF] hover:border-white/20 hover:text-white"
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

