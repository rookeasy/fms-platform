export type Building = {
  id: string;
  name: string;
  address: string;
  type: string;
  manager: string;
  healthScore: number;
  status: "Operational" | "Needs Review" | "At Risk";
  openItems: number;
  lastInspection: string;
};

export type TimelineItem = {
  title: string;
  date: string;
  description: string;
  tone?: "default" | "success" | "warning";
};

export const buildings: Building[] = [
  {
    id: "harbour-tower",
    name: "Harbour Tower",
    address: "88 Queens Quay W, Toronto",
    type: "Mixed Use",
    manager: "Avery Chen",
    healthScore: 92,
    status: "Operational",
    openItems: 4,
    lastInspection: "2026-06-12"
  },
  {
    id: "king-station",
    name: "King Station Offices",
    address: "21 King St E, Toronto",
    type: "Commercial",
    manager: "Maya Patel",
    healthScore: 76,
    status: "Needs Review",
    openItems: 11,
    lastInspection: "2026-06-04"
  },
  {
    id: "lakeside-residence",
    name: "Lakeside Residence",
    address: "1400 Lakeshore Blvd, Mississauga",
    type: "Residential",
    manager: "Noah Williams",
    healthScore: 61,
    status: "At Risk",
    openItems: 18,
    lastInspection: "2026-05-28"
  }
];

export const dashboardMetrics = [
  { label: "Buildings", value: "24", detail: "3 need review" },
  { label: "Open Work Orders", value: "148", detail: "22 due this week" },
  { label: "Inspections", value: "36", detail: "9 scheduled" },
  { label: "Certificates", value: "91%", detail: "current portfolio-wide" }
];

export const workOrders = [
  { id: "WO-1042", building: "Harbour Tower", priority: "Medium", status: "Open" },
  { id: "WO-1041", building: "King Station Offices", priority: "High", status: "In Review" },
  { id: "WO-1039", building: "Lakeside Residence", priority: "High", status: "Open" }
];

export const inspections = [
  { id: "IN-220", building: "Harbour Tower", type: "Annual", date: "2026-07-08" },
  { id: "IN-219", building: "King Station Offices", type: "Fire Safety", date: "2026-07-11" },
  { id: "IN-218", building: "Lakeside Residence", type: "Deficiency Follow-up", date: "2026-07-15" }
];

export const portfolioTimeline: TimelineItem[] = [
  {
    title: "Repository shell created",
    date: "2026-06-30",
    description: "Frontend routes and reusable components are mocked for review.",
    tone: "success"
  },
  {
    title: "Backend integration pending",
    date: "Next phase",
    description: "API contracts and real data loading have not been connected yet.",
    tone: "warning"
  },
  {
    title: "Business modules pending",
    date: "Future phase",
    description: "Domain workflows remain intentionally out of scope for this shell."
  }
];

export function getBuilding(buildingId: string) {
  return buildings.find((building) => building.id === buildingId) ?? buildings[0];
}
