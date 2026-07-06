type LoadingStateProps = {
  label: string;
};

export function LoadingState({ label }: LoadingStateProps) {
  return (
    <div className="space-y-3" aria-live="polite" aria-busy="true">
      <p className="text-sm font-semibold text-[#64748B]">{label}</p>
      <div className="grid gap-3 md:grid-cols-3">
        {[0, 1, 2].map((item) => (
          <div key={item} className="fop-card h-28 animate-pulse p-4">
            <div className="h-4 w-2/3 rounded bg-slate-200" />
            <div className="mt-4 h-3 w-full rounded bg-slate-100" />
            <div className="mt-2 h-3 w-4/5 rounded bg-slate-100" />
          </div>
        ))}
      </div>
    </div>
  );
}

