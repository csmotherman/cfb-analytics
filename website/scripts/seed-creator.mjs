#!/usr/bin/env node
// Insert one Creator Hub creator with a properly hashed PIN. Run once per
// creator; never hardcode a plaintext PIN in source.
//
// Usage:
//   node scripts/seed-creator.mjs "Darren Talks Ball" darren-talks-ball 1234
//
// Requires DATABASE_URL (or POSTGRES_URL) in the environment, e.g.:
//   DATABASE_URL="$(vercel env pull --yes /dev/stdout 2>/dev/null | grep -m1 DATABASE_URL | cut -d= -f2-)" node scripts/seed-creator.mjs ...
// or just export it directly from your Vercel project's Postgres settings.

import { neon } from "@neondatabase/serverless";
import { randomBytes, scryptSync } from "node:crypto";

const [name, slug, pin] = process.argv.slice(2);

if (!name || !slug || !pin) {
  console.error("Usage: node scripts/seed-creator.mjs \"Display Name\" slug 1234");
  process.exit(1);
}
if (!/^\d{4}$/.test(pin)) {
  console.error("PIN must be exactly 4 digits.");
  process.exit(1);
}

const connectionString = process.env.DATABASE_URL || process.env.POSTGRES_URL;
if (!connectionString) {
  console.error("Set DATABASE_URL or POSTGRES_URL first.");
  process.exit(1);
}

const salt = randomBytes(16).toString("hex");
const hash = scryptSync(pin, salt, 32).toString("hex");

const sql = neon(connectionString);
const rows = await sql`
  insert into creators (slug, name, pin_hash, pin_salt)
  values (${slug}, ${name}, ${hash}, ${salt})
  on conflict (slug) do update set name = excluded.name, pin_hash = excluded.pin_hash, pin_salt = excluded.pin_salt
  returning id, slug, name
`;

console.log(`Seeded creator: ${JSON.stringify(rows[0])}`);
