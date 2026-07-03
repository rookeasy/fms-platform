import { AppShell } from "@/components/AppShell";
import { PassportSection } from "@/components/PassportSection";
import { StatusBadge } from "@/components/StatusBadge";
import { fuzionBrand } from "@/lib/brand";

const recommendations = [
  "Review closeout packages with missing warranty, O&M, or ITM transition evidence.",
  "Prioritize properties with readiness below 80% before handover meetings.",
  "Convert completed handover buildings into service and inspection follow-up work."
];

export default function AdvisorPage() {
  return (
    <AppShell title="AI / Advisor">
      <div className="space-y-6">
        <section className="fop-card p-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="fop-label">Ask Fuzion</p>
              <h2 className="mt-2 text-2xl font-semibold tracking-normal text-white">Embedded operating intelligence</h2>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-[#B6C1CF]">
                Advisor is the shared entry point for project, property, closeout, and operational recommendations across {fuzionBrand.shortName}.
              </p>
            </div>
            <StatusBadge status="Placeholder" />
          </div>
        </section>

        <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
          <PassportSection title="Recommended Focus">
            <div className="space-y-3">
              {recommendations.map((recommendation) => (
                <div key={recommendation} className="rounded-xl border border-white/10 bg-white/[0.035] p-4 text-sm text-[#B6C1CF]">
                  {recommendation}
                </div>
              ))}
            </div>
          </PassportSection>

          <PassportSection title={fuzionBrand.tagline}>
            <div className="space-y-3">
              {fuzionBrand.brandPromise.map((item) => (
                <div key={item.label}>
                  <p className="text-sm font-semibold text-white">{item.label}</p>
                  <p className="text-sm text-[#B6C1CF]">{item.description}</p>
                </div>
              ))}
            </div>
          </PassportSection>
        </div>
      </div>
    </AppShell>
  );
}
