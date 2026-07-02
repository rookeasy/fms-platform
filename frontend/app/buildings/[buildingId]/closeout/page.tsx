import { AppShell } from "@/components/AppShell";
import { BuildingCloseoutClient } from "@/components/buildings/BuildingCloseoutClient";

type BuildingCloseoutPageProps = {
  params: { buildingId: string };
};

export default function BuildingCloseoutPage({ params }: BuildingCloseoutPageProps) {
  return (
    <AppShell title="Digital Closeout Package">
      <BuildingCloseoutClient buildingId={params.buildingId} />
    </AppShell>
  );
}
