import { createHmac, timingSafeEqual } from "node:crypto";
import { cookies } from "next/headers";

export const CREATOR_HUB_COOKIE_NAME = "mff_creator_hub";
const CREATOR_HUB_SESSION_PURPOSE = "mff-creator-hub-session-v1";

function configuredPassword(): string {
  return process.env.CREATOR_HUB_PASSWORD?.trim() ?? "";
}

function safeEqual(left: string, right: string): boolean {
  const leftBuffer = Buffer.from(left);
  const rightBuffer = Buffer.from(right);

  return leftBuffer.length === rightBuffer.length && timingSafeEqual(leftBuffer, rightBuffer);
}

function sessionToken(password: string): string {
  return createHmac("sha256", password).update(CREATOR_HUB_SESSION_PURPOSE).digest("hex");
}

export function isCreatorHubConfigured(): boolean {
  return configuredPassword().length > 0;
}

export function creatorHubPasswordMatches(submittedPassword: string): boolean {
  const expectedPassword = configuredPassword();
  return expectedPassword.length > 0 && safeEqual(submittedPassword, expectedPassword);
}

export function creatorHubSessionToken(): string | null {
  const password = configuredPassword();
  return password ? sessionToken(password) : null;
}

export async function hasCreatorHubAccess(): Promise<boolean> {
  const expectedToken = creatorHubSessionToken();
  if (!expectedToken) return false;

  const cookieStore = await cookies();
  const actualToken = cookieStore.get(CREATOR_HUB_COOKIE_NAME)?.value ?? "";
  return safeEqual(actualToken, expectedToken);
}
