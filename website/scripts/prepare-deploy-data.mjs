import fs from "node:fs";
import path from "node:path";

const websiteRoot=process.cwd();
const repositoryRoot=path.resolve(websiteRoot,"..");
const sourceRoot=path.join(repositoryRoot,"data","published");
const targetRoot=path.join(websiteRoot,".published-data");

const copyFile=(source,target)=>{
  if(!fs.existsSync(source))return false;
  fs.mkdirSync(path.dirname(target),{recursive:true});
  fs.copyFileSync(source,target);
  return true;
};

if(!fs.existsSync(sourceRoot)){
  throw new Error(`Published data directory not found: ${sourceRoot}`);
}

fs.rmSync(targetRoot,{recursive:true,force:true});
fs.mkdirSync(targetRoot,{recursive:true});

let files=0;

// /analytics remains server-rendered because ?year= selects the historical
// season at request time. Ship only the four artifacts that page actually reads.
for(const entry of fs.readdirSync(sourceRoot,{withFileTypes:true})){
  if(!entry.isDirectory()||!/^(201\d|202[0-5])$/.test(entry.name))continue;
  const season=entry.name;
  const sourceSeason=path.join(sourceRoot,season);
  const targetSeason=path.join(targetRoot,season);

  for(const name of ["season.json","games.json"]){
    if(copyFile(
      path.join(sourceSeason,"teams","michigan",name),
      path.join(targetSeason,"teams","michigan",name)
    ))files+=1;
  }

  if(copyFile(
    path.join(sourceSeason,"national","teams.json"),
    path.join(targetSeason,"national","teams.json")
  ))files+=1;

  if(copyFile(
    path.join(sourceSeason,"analytics","ridge-overview.json"),
    path.join(targetSeason,"analytics","ridge-overview.json")
  ))files+=1;
}

// Player profiles remain request-rendered because ?tab=stats changes the server
// output. Keep only the Michigan roster/profile files required by currentRoster()
// and the two verified career-stat artifacts used by the profile page.
const currentMichiganFiles=[
  "roster.json",
  "player-grades.json",
  "player-recruiting-ratings.json",
  "recruiting.json",
  "player-production-grades.json",
  "player-roster-status.json",
  "player-images.json",
  "player-profile-insights.json",
  "player-importance.json",
  "player-career-stats.json",
  "player-career-game-logs.json"
];
for(const name of currentMichiganFiles){
  if(copyFile(
    path.join(sourceRoot,"2026","michigan",name),
    path.join(targetRoot,"2026","michigan",name)
  ))files+=1;
}

if(copyFile(
  path.join(sourceRoot,"directory_history","players","current-by-team","michigan.json"),
  path.join(targetRoot,"directory_history","players","current-by-team","michigan.json")
))files+=1;

const bytes=(root)=>{
  let total=0;
  if(!fs.existsSync(root))return total;
  for(const entry of fs.readdirSync(root,{withFileTypes:true})){
    const file=path.join(root,entry.name);
    total+=entry.isDirectory()?bytes(file):fs.statSync(file).size;
  }
  return total;
};

const sizeMb=bytes(targetRoot)/1024/1024;
console.log(`Prepared ${files} route-specific runtime JSON files (${sizeMb.toFixed(1)} MB) in ${targetRoot}`);
if(sizeMb>20){
  throw new Error(`Runtime data bundle is unexpectedly large (${sizeMb.toFixed(1)} MB). Refusing to build.`);
}
