import { StatusBadge } from "@/components/StatusBadge";

type ReadinessChecklistProps = {
  items: Array<{ key?: string; label: string; complete: boolean }>;
};

export function ReadinessChecklist({ items }: ReadinessChecklistProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <h4 className="font-semibold text-slate-950">Property Readiness Checklist</h4>
      <div className="mt-4 space-y-3">
        {items.map((item) => (
          <div key={item.key ?? item.label} className="flex items-center justify-between gap-3 text-sm">
            <span className="text-slate-700">{item.label}</span>
            <StatusBadge status={item.complete ? "Complete" : "Missing"} />
          </div>
        ))}
      </div>
    </div>
  );
}
