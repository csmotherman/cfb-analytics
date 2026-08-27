"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { getCreatorById, getCreatorBySlug } from "../../lib/creator-hub/db";
import { createSession, destroySessionToken, getSessionCreator, verifyPin, SESSION_COOKIE_NAME } from "../../lib/creator-hub/auth";

export async function unlockCreator(formData: FormData): Promise<void> {
  const creatorId = Number(formData.get("creatorId"));
  const pin = String(formData.get("pin") || "");
  const creator = Number.isFinite(creatorId) ? await getCreatorById(creatorId) : null;

  if (!creator || !verifyPin(pin, creator.pin_hash, creator.pin_salt)) {
    const slug = creator?.slug ?? "";
    redirect(`/creator-hub?error=invalid&creator=${encodeURIComponent(slug)}`);
  }

  const token = await createSession(creator.id);
  const store = await cookies();
  store.set(SESSION_COOKIE_NAME, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/creator-hub",
    maxAge: 60 * 60 * 24 * 30,
  });
  redirect(`/creator-hub/${creator.slug}`);
}

export async function lockCreator(): Promise<void> {
  const store = await cookies();
  const token = store.get(SESSION_COOKIE_NAME)?.value;
  if (token) await destroySessionToken(token);
  store.set(SESSION_COOKIE_NAME, "", { path: "/creator-hub", expires: new Date(0) });
  redirect("/creator-hub");
}

export async function requireCreatorForSlug(slug: string) {
  const session = await getSessionCreator();
  if (!session || session.slug !== slug) {
    redirect("/creator-hub");
  }
  return session;
}

export async function resolveCreatorOrRedirect(slug: string) {
  const creator = await getCreatorBySlug(slug);
  if (!creator) redirect("/creator-hub");
  return creator;
}
