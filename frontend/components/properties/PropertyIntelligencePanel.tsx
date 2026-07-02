"use client";

import { PropertyIntelligenceWorkspace } from "@/components/properties/intelligence/PropertyIntelligenceWorkspace";
import type { PropertyIntelligence } from "@/lib/fms-api";

type PropertyIntelligencePanelProps = {
  intelligence: PropertyIntelligence;
};

export function PropertyIntelligencePanel({ intelligence }: PropertyIntelligencePanelProps) {
  return <PropertyIntelligenceWorkspace intelligence={intelligence} />;
}
