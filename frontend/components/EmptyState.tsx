import type { ReactNode } from "react";

type EmptyStateProps = {
  title: string;
  message: string;
  action?: ReactNode;
};

export function EmptyState({ title, message, action }: EmptyStateProps) {
  return (
    <section className="rounded-2xl border border-dashed border-[#CBD5E1] bg-[#F8FAFC] p-8 text-center">
      <h2 className="text-lg font-semibold tracking-normal text-[#0F172A]">{title}</h2>
      <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-[#64748B]">{message}</p>
      {action ? <div className="mt-5 flex justify-center">{action}</div> : null}
    </section>
  );
}
