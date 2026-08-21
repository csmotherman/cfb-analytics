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

const copyTree=(source,target)=>{
  if(!fs.existsSync(source))return 0;
  let count=0;
  for(const entry of fs.readdirSync(source,{withFileTypes:true})){
    const from=path.join(source,entry.name);
    const to=path.join(target,entry.name);
    if(entry.isDirectory())count+=copyTree(from,to);
    else if(entry.isFile()&&entry.name.endsWith(".json")){copyFile(from,to);count+=1;}
  }
  return count;
};

if(!fs.existsSync(sourceRoot)){
  throw new Error(`Published data directory not found: ${sourceRoot}`);
}

fs.rmSync(targetRoot,{recursive:true,force:true});
fs.mkdirSync(targetRoot,{recursive:true});

let files=0;

// Current-season product data is small enough to ship as a complete season tree.
files+=copyTree(path.join(sourceRoot,"2026"),path.join(targetRoot,"2026"));

// Historical pages only need Michigan, national comparisons and the compact
// opponent-adjusted overview. Never copy directory_history into deployment.
for(const entry of fs.readdirSync(sourceRoot,{withFileTypes:true})){
  if(!entry.isDirectory()||!/^(201\d|202[0-5])$/.test(entry.name))continue;
  const season=entry.name;
  const sourceSeason=path.join(sourceRoot,season);
  const targetSeason=path.join(targetRoot,season);

  files+=copyTree(path.join(sourceSeason,"teams","michigan"),path.join(targetSeason,"teams","michigan"));

  for(const name of ["teams.json","rankings.json","conferences.json"]){
    if(copyFile(path.join(sourceSeason,"national",name),path.join(targetSeason,"national",name)))files+=1;
  }

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
console.log(`Prepared ${files} deployment JSON files (${sizeMb.toFixed(1)} MB) in ${targetRoot}`);
if(sizeMb>120){
  throw new Error(`Deployment data bundle is unexpectedly large (${sizeMb.toFixed(1)} MB). Refusing to build.`);
}
