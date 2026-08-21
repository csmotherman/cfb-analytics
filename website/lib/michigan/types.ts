export type ValueType = "ACTUAL" | "PROJECTED" | "PRESEASON" | "BENCHMARK";
export type Grade = "F" | "D" | "C" | "B" | "A" | "S" | "S+";
export type PlayerInsight = {
  valueType: "PROJECTED";
  focus: {kind:"PRODUCTION"|"PROSPECT";label:string;grade?:Grade|null;stars?:number|null;rating?:number|null;percentile?:number|null};
  pastSeasons: Array<{season:number;team:string;stats:Array<{label:string;value:number}>}>;
  strengths: string[]; growthAreas: string[]; expectation: string; expectationBasis: string;
};

export type MichiganPlayer = {
  id: string; firstName: string; lastName: string; jersey?: number | null;
  position?: string | null; height?: number | null; weight?: number | null;
  year?: number | null; homeCity?: string | null; homeState?: string | null;
  teamId: number; season: number; valueType: ValueType; recruitIds?: string[];
  playerImageUrl?: string | null; playerImageSource?: string | null;
  playerImageSourceUrl?: string | null;
  playerImageCredit?: string | null; playerImageUpdatedAt?: string | null;
  performanceGrade?: Grade | null; prospectGrade?: Grade | null; potentialGrade?: Grade | null;
  performanceGradeBasis?: string | null; performanceGradeSeason?: number | null;
  productionPercentile?: number | null; usagePercentile?: number | null; nationalPositionPercentile?: number | null;
  productionScore?: number | null; usageValue?: number | null; productionCohortSize?: number | null; positionFamily?: string | null;
  rosterStatus?: "RETURNING" | "TRANSFER" | "FRESHMAN" | "UNCLASSIFIED" | null; previousTeam?: string | null;
  compositeRating?: number | null; stars?: number | null; nationalRecruitRank?: number | null;
  gradeBasis?: string | null;
  recruitClass?: number | null; originalCommitment?: string | null;
  careerTimeline?: Array<{season:number;team?:string|null;position?:string|null;jersey?:number|null;year?:number|null}>;
  insight?: PlayerInsight | null;
  importanceRank?: number | null; importanceRole?: string | null; importanceTier?: string | null; importanceReason?: string | null;
};

export type MichiganRecruit = {
  id: string; athleteId?: string | null; year: number; ranking?: number | null; name: string;
  school?: string | null; position?: string | null; height?: number | null; weight?: number | null;
  committedTo?: string | null;
  stars?: number | null; rating?: number | null; city?: string | null; stateProvince?: string | null;
  grade?: Grade | null; valueType: ValueType; source: string;
};

export type RecruitingClass = {
  season: number; team: string; ranking?: { rank?: number; points?: number } | null;
  recruits: MichiganRecruit[]; valueType: ValueType;
};

export type MichiganScheduleGame = {
  id: number; season: number; week: number; startDate: string; startTimeTBD: boolean;
  completed: boolean; neutralSite: boolean; conferenceGame: boolean; venue?: string | null;
  homeId: number; homeTeam: string; homePoints?: number | null;
  awayId: number; awayTeam: string; awayPoints?: number | null; valueType: ValueType;
};