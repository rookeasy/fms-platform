import type { TimelineItem } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

type TimelineProps = {
  items: TimelineItem[];
};

export function Timeline({ items }: TimelineProps) {
  return (
    <ol className="space-y-4">
      {items.map((item) => (
        <li key={`${item.title}-${item.date}`} className="flex gap-3">
          <span
            className={cn(
              "mt-1 h-3 w-3 shrink-0 rounded-full",
              item.tone === "success"
                ? "bg-emerald-500"
                : item.tone === "warning"
                  ? "bg-amber-500"
                  : "bg-slate-400"
            )}
          />
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <p className="font-medium text-[#0F172A]">{item.title}</p>
              <p className="text-xs font-medium uppercase text-[#64748B]">{item.date}</p>
            </div>
            <p className="mt-1 text-sm leading-6 text-[#334155]">{item.description}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}
