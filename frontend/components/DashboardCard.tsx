import type { ReactNode } from "react";

type DashboardCardProps = {
  title: string;
  value: string;
  detail?: string;
  children?: ReactNode;
};

export function DashboardCard({ title, value, detail, children }: DashboardCardProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <p className="mt-2 text-3xl font-semibold text-slate-950">{value}</p>
          {detail ? <p className="mt-2 text-sm text-slate-600">{detail}</p> : null}
        </div>
        {children}
      </div>
    </section>
  );
}
