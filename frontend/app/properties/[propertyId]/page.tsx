import { AppShell } from "@/components/AppShell";
import { PropertyDetailClient } from "@/components/properties/PropertyDetailClient";

type PropertyDetailPageProps = {
  params: { propertyId: string };
};

export default function PropertyDetailPage({ params }: PropertyDetailPageProps) {
  return (
    <AppShell title="Property">
      <PropertyDetailClient propertyId={params.propertyId} />
    </AppShell>
  );
}
