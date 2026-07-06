import type { ReactNode } from "react";

type DashboardCardProps = {
  title: string;
  value: string;
  detail?: string;
  children?: ReactNode;
};

export function DashboardCard({ title, value, detail, children }: DashboardCardProps) {
  return (
    <section className="fop-card p-5 transition hover:-translate-y-0.5 hover:shadow-xl">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="fop-label">{title}</p>
          <p className="mt-3 text-3xl font-semibold tracking-normal text-[#0F172A]">{value}</p>
          {detail ? <p className="mt-2 text-sm text-[#64748B]">{detail}</p> : null}
        </div>
        {children}
      </div>
    </section>
  );
}
