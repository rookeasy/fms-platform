import { AppShell } from "@/components/AppShell";
import { BuildingProfileClient } from "@/components/buildings/BuildingProfileClient";

type BuildingDetailPageProps = {
  params: { buildingId: string };
};

export default function BuildingDetailPage({ params }: BuildingDetailPageProps) {
  return (
    <AppShell title="Building Profile">
      <BuildingProfileClient buildingId={params.buildingId} />
    </AppShell>
  );
}
