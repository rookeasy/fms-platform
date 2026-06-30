import { AppShell } from "@/components/AppShell";
import { DashboardCard } from "@/components/DashboardCard";

export default function ReportsPage() {
  return (
    <AppShell title="Reports">
      <div className="grid gap-4 md:grid-cols-3">
        <DashboardCard title="Portfolio Summary" value="Draft" detail="Mock report tile" />
        <DashboardCard title="Compliance Trend" value="Draft" detail="Mock report tile" />
        <DashboardCard title="Work Order Aging" value="Draft" detail="Mock report tile" />
      </div>
    </AppShell>
  );
}
