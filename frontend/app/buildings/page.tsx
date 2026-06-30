import { AppShell } from "@/components/AppShell";
import { BuildingCard } from "@/components/BuildingCard";
import { buildings } from "@/lib/mock-data";

export default function BuildingsPage() {
  return (
    <AppShell title="Buildings">
      <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
        {buildings.map((building) => (
          <BuildingCard key={building.id} building={building} />
        ))}
      </div>
    </AppShell>
  );
}
