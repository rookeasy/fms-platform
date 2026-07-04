export type ProjectStatus = "completed_occupied" | "active";
export type LifecycleStage = "build" | "advise" | "protect";

export type Building = {
  id: string;
  jobNo: string;
  projectName: string;
  passportNo: string;
  name: string;
  address: string;
  city: string;
  type: string;
  manager: string;
  healthScore: number;
  status: ProjectStatus;
  lifecycleStage: LifecycleStage;
  projectStatus: "Completed / Occupied" | "Active";
  occupancyStatus: "Occupied" | "Pre-occupancy";
  passportStatus: "Active Record" | "In Progress";
  closeoutStatus: "Archived / Operating" | "Open";
  inspectionStatus: "Current / Historical" | "Pending / In Progress";
  openItems: number;
  lastInspection: string;
};

export type TimelineItem = {
  title: string;
  date: string;
  description: string;
  tone?: "default" | "success" | "warning";
};

const completedProjects = [
  ["5000", "Parkway Lofts Bldgs A-B-C", "St. Catharines"],
  ["5002", "Montebello", "St. Catharines"],
  ["5003", "Picasso Condos", "Richmond Hill"],
  ["5004", "SOHO Bldgs A & B", "Hamilton"],
  ["5005", "Gilmore LTC", "Fort Erie"],
  ["5006", "Heritage Green Ph 2 Bldgs 1-3", "Hamilton"],
  ["5007", "Maya Stacked Towns", "Brampton"],
  ["5008", "Urbane Communities", "Niagara Falls"],
  ["5009", "Women & Children Housing", "Fort Erie"],
  ["5010", "Radiant Care Pleasant Manor LTC", "NOTL"],
  ["5011", "Childcare Addition at Banbury Heights School", "Brantford"],
  ["5012", "Northern Green Dry Room TFO", "Brampton"],
  ["5013", "Hagersville Library", "Hagersville"],
  ["5014", "Bldg. 3 Base Bldg. & Site @ 18 Rose Ave", "Welland"],
  ["5015", "Rosenberg Elementary School & Community Centre", "Kitchener"],
  ["5017", "MetalWorks Condo PH4", "Guelph"],
  ["5018", "JBL Building Expansion", "Port Colborne"],
  ["5020", "Elevate Condos", "Kitchener"],
  ["5021", "Royal Canadian Polish Legion", "St. Catharines"],
  ["5025", "North Green CuraLeaf Supply & Install CuraLeaf", "Brampton"]
] as const;

const activeProjects = [
  ["5001", "Linhaven LTC", "St. Catharines"],
  ["5016", "Stanley Self Storage (Dunkirk)", "St. Catharines"],
  ["5019", "Niagara St. Plaza", "Welland"],
  ["5022", "Daycare Expansion at Pavillon de la Jeunesse", "Hamilton"],
  ["5023", "Ladona River Bldg B", "Niagara Falls"],
  ["5024", "320 Geneva Street Phase 1", "St. Catharines"],
  ["5026", "HNHC 311 Ramsey Dr", "Dunnville"],
  ["5027", "AHI Expansion @ NC", "Welland"]
] as const;

function slugify(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

function scoreFor(jobNo: string, status: ProjectStatus) {
  const offset = Number(jobNo) % (status === "completed_occupied" ? 19 : 41);
  return status === "completed_occupied" ? 78 + offset : 45 + offset;
}

function projectRecord([jobNo, projectName, city]: readonly [string, string, string], status: ProjectStatus): Building {
  const isCompleted = status === "completed_occupied";
  return {
    id: jobNo,
    jobNo,
    projectName,
    passportNo: `FPP-${jobNo}`,
    name: projectName,
    address: city,
    city,
    type: "Fuzion Project",
    manager: "Fuzion Tech Inc.",
    healthScore: scoreFor(jobNo, status),
    status,
    lifecycleStage: isCompleted ? "protect" : "build",
    projectStatus: isCompleted ? "Completed / Occupied" : "Active",
    occupancyStatus: isCompleted ? "Occupied" : "Pre-occupancy",
    passportStatus: isCompleted ? "Active Record" : "In Progress",
    closeoutStatus: isCompleted ? "Archived / Operating" : "Open",
    inspectionStatus: isCompleted ? "Current / Historical" : "Pending / In Progress",
    openItems: isCompleted ? Number(jobNo) % 4 : 3 + (Number(jobNo) % 9),
    lastInspection: isCompleted ? "Historical" : "Pending / In Progress"
  };
}

export const buildings: Building[] = [
  ...completedProjects.map((project) => projectRecord(project, "completed_occupied")),
  ...activeProjects.map((project) => projectRecord(project, "active"))
];

export const dashboardMetrics = [
  { label: "Fuzion Projects", value: `${buildings.length}`, detail: `${activeProjects.length} active` },
  { label: "Completed / Occupied", value: `${completedProjects.length}`, detail: "operating records" },
  { label: "Active Projects", value: `${activeProjects.length}`, detail: "open delivery records" },
  { label: "Passport Records", value: `${buildings.length}`, detail: "FPP job-linked" }
];

export const lifecycleSummary = {
  build: buildings.filter((building) => building.lifecycleStage === "build").length,
  advise: buildings.filter((building) => building.lifecycleStage === "advise").length,
  protect: buildings.filter((building) => building.lifecycleStage === "protect").length,
  averageBuildingHealthIndex: Math.round(buildings.reduce((total, building) => total + building.healthScore, 0) / buildings.length),
  lowestProtectionScores: [...buildings].sort((a, b) => a.healthScore - b.healthScore).slice(0, 5),
  overdueComplianceItems: buildings.filter((building) => building.status === "active").slice(0, 4)
};

export const workOrders = activeProjects.slice(0, 5).map(([jobNo, projectName, city]) => ({
  id: `WO-${jobNo}`,
  jobNo,
  passportNo: `FPP-${jobNo}`,
  building: projectName,
  city,
  priority: Number(jobNo) % 2 === 0 ? "Medium" : "High",
  status: "Active"
}));

export const inspections = buildings.slice(0, 8).map((building) => ({
  id: `IN-${building.jobNo}`,
  jobNo: building.jobNo,
  passportNo: building.passportNo,
  building: building.projectName,
  type: building.status === "active" ? "Pending / In Progress" : "Current / Historical",
  date: building.lastInspection
}));

export const portfolioTimeline: TimelineItem[] = [
  {
    title: "Fuzion project records loaded",
    date: "Current",
    description: "Portfolio views now use active and completed Fuzion projects only.",
    tone: "success"
  },
  {
    title: "Passport numbering aligned",
    date: "Current",
    description: "Passport No. evolves from Job No. using FPP-<jobNo>.",
    tone: "success"
  },
  {
    title: "Operational placeholders",
    date: "MVP",
    description: "Missing non-sensitive fields use conservative operational placeholders.",
    tone: "warning"
  }
];

export const projectEvents = buildings.map((building) => ({
  projectId: `PRJ-${building.jobNo}`,
  jobNo: building.jobNo,
  projectName: building.projectName,
  city: building.city,
  status: building.projectStatus,
  lifecycleStage: building.lifecycleStage,
  linkedPassports: [building.passportNo],
  buildingIds: [building.id]
}));

export function getBuilding(buildingId: string) {
  return buildings.find((building) => building.id === buildingId || slugify(building.name) === buildingId) ?? buildings[0];
}
