import type { ReactNode } from "react";

type PassportSectionProps = {
  title: string;
  description?: string;
  children: ReactNode;
};

export function PassportSection({ title, description, children }: PassportSectionProps) {
  return (
    <section className="fop-card p-5">
      <div className="mb-4">
        <h2 className="text-lg font-semibold tracking-normal text-[#0F172A]">{title}</h2>
        {description ? <p className="mt-1 text-sm text-[#64748B]">{description}</p> : null}
      </div>
      {children}
    </section>
  );
}
