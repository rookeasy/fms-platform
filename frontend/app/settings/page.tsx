import { AppShell } from "@/components/AppShell";
import { PassportSection } from "@/components/PassportSection";
import { fuzionBrand } from "@/lib/brand";

export default function SettingsPage() {
  return (
    <AppShell title="Settings">
      <PassportSection title="Workspace Settings" description="Static controls for frontend shell review.">
        <div className="grid gap-4 md:grid-cols-2">
          <label className="block">
            <span className="text-sm font-medium text-[#B6C1CF]">Workspace name</span>
            <input className="mt-2 h-11 w-full rounded-md border border-white/15 px-3" defaultValue={fuzionBrand.product} />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-[#B6C1CF]">Default region</span>
            <input className="mt-2 h-11 w-full rounded-md border border-white/15 px-3" defaultValue="Canada East" />
          </label>
        </div>
      </PassportSection>
    </AppShell>
  );
}

