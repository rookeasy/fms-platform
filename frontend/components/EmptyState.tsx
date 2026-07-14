import type { ReactNode } from "react";

type EmptyStateProps = {
  title: string;
  message: string;
  action?: ReactNode;
};

export function EmptyState({ title, message, action }: EmptyStateProps) {
  return (
    <section className="rounded-xl border border-dashed border-[color:var(--fop-build)]/35 bg-[color:var(--fop-build-soft)] p-8 text-center">
      <div className="mx-auto mb-4 h-10 w-10 rounded-md border-2 border-[color:var(--fop-build)] bg-white" aria-hidden="true" />
      <h2 className="text-lg font-semibold tracking-normal text-[color:var(--text-primary)]">{title}</h2>
      <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-[color:var(--text-secondary)]">{message}</p>
      {action ? <div className="mt-5 flex justify-center">{action}</div> : null}
    </section>
  );
}
