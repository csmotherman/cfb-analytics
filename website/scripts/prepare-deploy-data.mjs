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

// Keep the Vercel runtime bundle deliberately small. Finite Michigan pages
// (games, players, articles and position rooms) are prerendered at build time
// and can read directly from the repository checkout while Next builds them.
// The only route that still needs published JSON at request time is /analytics,
// whose year query parameter selects among historical seasons.
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
console.log(`Prepared ${files} runtime JSON files (${sizeMb.toFixed(1)} MB) in ${targetRoot}`);
if(sizeMb>20){
  throw new Error(`Runtime data bundle is unexpectedly large (${sizeMb.toFixed(1)} MB). Refusing to build.`);
}
