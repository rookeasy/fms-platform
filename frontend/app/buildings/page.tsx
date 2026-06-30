import { AppShell } from "@/components/AppShell";
import { BuildingRegistryClient } from "@/components/buildings/BuildingRegistryClient";

export default function BuildingsPage() {
  return (
    <AppShell title="Buildings">
      <BuildingRegistryClient />
    </AppShell>
  );
}
