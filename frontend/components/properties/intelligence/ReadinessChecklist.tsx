import { StatusBadge } from "@/components/StatusBadge";

type ReadinessChecklistProps = {
  items: Array<{ key?: string; label: string; complete: boolean }>;
};

export function ReadinessChecklist({ items }: ReadinessChecklistProps) {
  return (
    <div className="fop-card p-5">
      <h4 className="font-semibold tracking-normal text-white">Property Readiness Checklist</h4>
      <div className="mt-4 space-y-3">
        {items.map((item) => (
          <div key={item.key ?? item.label} className="flex items-center justify-between gap-3 text-sm">
            <span className="text-[#B6C1CF]">{item.label}</span>
            <StatusBadge status={item.complete ? "Complete" : "Missing"} />
          </div>
        ))}
      </div>
    </div>
  );
}

