import fs from "node:fs";
import path from "node:path";

type CachedJson = { mtimeMs: number; size: number; value: unknown };
const jsonCache = new Map<string, CachedJson>();

function publishedFile(segments:string[]){
  const relative=segments.slice(2);
  const bundled=path.join(process.cwd(),".published-data",...relative);
  if(fs.existsSync(bundled))return bundled;

  const repository=path.join(process.cwd(),"..","data","published",...relative);
  // Local development can still read the canonical repository data when the
  // compact deployment bundle has not been prepared yet.
  return repository;
}

export function readJson<T>(...segments: string[]): T | null {
  if (segments[0] !== "data" || segments[1] !== "published") {
    throw new Error(`Published-data path must begin with data/published: ${segments.join("/")}`);
  }
  if (segments.some((segment) => path.isAbsolute(segment) || segment === ".." || segment.includes("/../"))) {
    throw new Error(`Published-data path escapes the repository: ${segments.join("/")}`);
  }
  const file = publishedFile(segments);
  if (!fs.existsSync(file)) return null;
  try {
    const stats = fs.statSync(file);
    const cached = jsonCache.get(file);
    if (cached && cached.mtimeMs === stats.mtimeMs && cached.size === stats.size) return cached.value as T;
    const value = JSON.parse(fs.readFileSync(file, "utf8")) as T;
    jsonCache.set(file, { mtimeMs: stats.mtimeMs, size: stats.size, value });
    return value;
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    throw new Error(`Invalid published JSON at ${file}: ${reason}`, { cause: error });
  }
}

export function readConfigJson<T>(filename: string): T | null {
  if (path.basename(filename) !== filename || !filename.endsWith(".json")) throw new Error(`Invalid config filename: ${filename}`);
  const repository=path.join(process.cwd(),"..","src","cfb_analytics","config",filename);
  const bundled=path.join(process.cwd(),".published-data","_config",filename);
  const file=fs.existsSync(repository)?repository:bundled;
  if (!fs.existsSync(file)) return null;
  try {
    return JSON.parse(fs.readFileSync(file, "utf8")) as T;
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    throw new Error(`Invalid config JSON at ${file}: ${reason}`, { cause: error });
  }
}
