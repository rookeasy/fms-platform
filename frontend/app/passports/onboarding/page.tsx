import { AppShell } from "@/components/AppShell";
import { PassportOnboardingQueueClient } from "@/components/passports/PassportOnboardingQueueClient";

export default function PassportOnboardingPage() {
  return (
    <AppShell title="Completed Project Onboarding">
      <PassportOnboardingQueueClient />
    </AppShell>
  );
}
