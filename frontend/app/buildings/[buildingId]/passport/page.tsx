import { AppShell } from "@/components/AppShell";
import { BuildingPassportClient } from "@/components/buildings/BuildingPassportClient";

type BuildingPassportPageProps = {
  params: { buildingId: string };
};

export default function BuildingPassportPage({ params }: BuildingPassportPageProps) {
  return (
    <AppShell title="Building Protection Passport">
      <BuildingPassportClient buildingId={params.buildingId} />
    </AppShell>
  );
}
