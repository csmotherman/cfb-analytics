export type StoryTagType = "POSITION"|"UNIT"|"TOPIC";
export type StoryTag = {type:StoryTagType;slug:string;label:string};
export type StoryDataLink = {label:string;href:string;description:string};
export type MichiganStory = {
  slug:string;
  eyebrow:string;
  title:string;
  deck:string;
  body:string[];
  playerIds?:string[];
  published?:string;
  readMinutes?:number;
  tags:StoryTag[];
  dataLinks:StoryDataLink[];
  coverQuestion?:string;
  coverLabel?:string;
  coverTheme?:string;
  sources?:{label:string;url:string}[];
};

// Editorial reset: no published stories are live right now.
export function michiganStories(): MichiganStory[] {
  return [];
}

export function storyBySlug(slug:string): MichiganStory | null {
  return michiganStories().find(story=>story.slug===slug)??null;
}
