import { randomBytes, scryptSync, timingSafeEqual } from "node:crypto";
import { cookies } from "next/headers";
import { sql, type Creator } from "./db";

export const SESSION_COOKIE_NAME = "mff_creator_session";
const SESSION_TTL_MS = 1000 * 60 * 60 * 24 * 30; // 30 days

// scrypt's own cost (~tens of ms per attempt) is the brute-force mitigation
// here, not a lockout system -- this is a private, low-stakes tool for a
// handful of known creators, not a public account system. Keeping this
// simple is deliberate, matching the product spec's own "no traditional
// account is required" framing.
function derivePin(pin: string, salt: string): Buffer {
  return scryptSync(pin, salt, 32);
}

export function hashPin(pin: string): { hash: string; salt: string } {
  const salt = randomBytes(16).toString("hex");
  const hash = derivePin(pin, salt).toString("hex");
  return { hash, salt };
}

export function verifyPin(pin: string, hash: string, salt: string): boolean {
  const expected = Buffer.from(hash, "hex");
  const actual = derivePin(pin, salt);
  if (expected.length !== actual.length) return false;
  return timingSafeEqual(expected, actual);
}

export async function createSession(creatorId: number): Promise<string> {
  const token = randomBytes32Hex();
  const expiresAt = new Date(Date.now() + SESSION_TTL_MS).toISOString();
  await sql()`
    insert into creator_sessions (token, creator_id, expires_at)
    values (${token}, ${creatorId}, ${expiresAt})
  `;
  return token;
}

export async function destroySessionToken(token: string): Promise<void> {
  await sql()`delete from creator_sessions where token = ${token}`;
}

export async function getSessionCreator(): Promise<Creator | null> {
  const store = await cookies();
  const token = store.get(SESSION_COOKIE_NAME)?.value;
  if (!token) return null;

  const rows = await sql()`
    select creators.* from creator_sessions
    join creators on creators.id = creator_sessions.creator_id
    where creator_sessions.token = ${token} and creator_sessions.expires_at > now()
    limit 1
  `;
  return (rows as Creator[])[0] ?? null;
}

function randomBytes32Hex(): string {
  return randomBytes(32).toString("hex");
}
