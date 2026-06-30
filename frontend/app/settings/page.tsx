import { AppShell } from "@/components/AppShell";
import { PassportSection } from "@/components/PassportSection";

export default function SettingsPage() {
  return (
    <AppShell title="Settings">
      <PassportSection title="Workspace Settings" description="Static controls for frontend shell review.">
        <div className="grid gap-4 md:grid-cols-2">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Workspace name</span>
            <input className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3" defaultValue="FMS Platform" />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Default region</span>
            <input className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3" defaultValue="Canada East" />
          </label>
        </div>
      </PassportSection>
    </AppShell>
  );
}
