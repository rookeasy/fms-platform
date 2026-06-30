import type { ReactNode } from "react";

type PassportSectionProps = {
  title: string;
  description?: string;
  children: ReactNode;
};

export function PassportSection({ title, description, children }: PassportSectionProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-slate-950">{title}</h2>
        {description ? <p className="mt-1 text-sm text-slate-600">{description}</p> : null}
      </div>
      {children}
    </section>
  );
}
