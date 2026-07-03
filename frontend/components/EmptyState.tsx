import type { ReactNode } from "react";

type EmptyStateProps = {
  title: string;
  message: string;
  action?: ReactNode;
};

export function EmptyState({ title, message, action }: EmptyStateProps) {
  return (
    <section className="rounded-2xl border border-dashed border-white/15 bg-white/[0.035] p-8 text-center">
      <h2 className="text-lg font-semibold tracking-normal text-white">{title}</h2>
      <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-[#B6C1CF]">{message}</p>
      {action ? <div className="mt-5 flex justify-center">{action}</div> : null}
    </section>
  );
}
