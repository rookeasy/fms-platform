import { AppShell } from "@/components/AppShell";
import { BuildingLibraryIndexClient } from "@/components/buildings/BuildingLibraryIndexClient";

export default function DocumentsPage() {
  return (
    <AppShell title="Building Library">
      <BuildingLibraryIndexClient />
    </AppShell>
  );
}
