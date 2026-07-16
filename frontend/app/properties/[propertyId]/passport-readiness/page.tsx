import { AppShell } from "@/components/AppShell";
import { SohoPassportReadinessClient } from "@/components/properties/SohoPassportReadinessClient";

type SohoPassportReadinessPageProps = {
  params: { propertyId: string };
};

export default function SohoPassportReadinessPage({ params }: SohoPassportReadinessPageProps) {
  return (
    <AppShell title="SOHO Passport Readiness">
      <SohoPassportReadinessClient propertyId={params.propertyId} />
    </AppShell>
  );
}
