import { AppShell } from "@/components/AppShell";
import { BuildingLibraryClient } from "@/components/buildings/BuildingLibraryClient";

type BuildingLibraryPageProps = {
  params: { buildingId: string };
};

export default function BuildingLibraryPage({ params }: BuildingLibraryPageProps) {
  return (
    <AppShell title="Building Library">
      <BuildingLibraryClient buildingId={params.buildingId} />
    </AppShell>
  );
}
