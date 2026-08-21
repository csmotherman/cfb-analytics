export type MichiganPollSnapshot={
  apRank:number|null;
  coachesRank:number|null;
  modelRank:number|null;
  modelStatus:string;
  label:string;
};

// Preseason snapshot. AP and Coaches rankings are public polls; the model stays
// intentionally unavailable until enough current-season games exist to support
// a meaningful opponent-adjusted ranking.
export const michiganPollSnapshot:MichiganPollSnapshot={
  apRank:16,
  coachesRank:16,
  modelRank:null,
  modelStatus:"Starts Week 4",
  label:"2026 preseason",
};
