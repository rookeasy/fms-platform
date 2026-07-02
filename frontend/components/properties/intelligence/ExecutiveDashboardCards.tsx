import { AlertTriangle, BarChart3, ClipboardCheck, FileText, ShieldCheck } from "lucide-react";

import { IntelligenceScoreCard } from "@/components/properties/intelligence/IntelligenceScoreCard";
import type { PropertyIntelligence } from "@/lib/fms-api";

type ExecutiveDashboardCardsProps = {
  intelligence: PropertyIntelligence;
};

export function ExecutiveDashboardCards({ intelligence }: ExecutiveDashboardCardsProps) {
  return (
    <div className="grid gap-4 lg:grid-cols-5">
      <IntelligenceScoreCard score={intelligence.health} icon={BarChart3} />
      <IntelligenceScoreCard score={intelligence.confidence} icon={ShieldCheck} />
      <IntelligenceScoreCard score={intelligence.risk} icon={AlertTriangle} />
      <IntelligenceScoreCard score={intelligence.readiness} icon={ClipboardCheck} />
      <IntelligenceScoreCard score={intelligence.passport} icon={FileText} />
    </div>
  );
}
