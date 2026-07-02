import { AppShell } from "@/components/AppShell";
import { PropertyCampusClient } from "@/components/properties/PropertyCampusClient";

export default function PropertiesPage() {
  return (
    <AppShell title="Properties">
      <PropertyCampusClient />
    </AppShell>
  );
}
