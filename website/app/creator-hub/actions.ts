"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import {
  CREATOR_HUB_COOKIE_NAME,
  creatorHubPasswordMatches,
  creatorHubSessionToken,
  isCreatorHubConfigured,
} from "../../lib/creator-hub-auth";

const TWO_WEEKS = 60 * 60 * 24 * 14;

export async function unlockCreatorHub(formData: FormData) {
  if (!isCreatorHubConfigured()) {
    redirect("/creator-hub?error=setup");
  }

  const submittedPassword = String(formData.get("password") ?? "");
  if (!creatorHubPasswordMatches(submittedPassword)) {
    redirect("/creator-hub?error=invalid");
  }

  const token = creatorHubSessionToken();
  if (!token) {
    redirect("/creator-hub?error=setup");
  }

  const cookieStore = await cookies();
  cookieStore.set(CREATOR_HUB_COOKIE_NAME, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/creator-hub",
    maxAge: TWO_WEEKS,
  });

  redirect("/creator-hub");
}

export async function lockCreatorHub() {
  const cookieStore = await cookies();
  cookieStore.set(CREATOR_HUB_COOKIE_NAME, "", {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/creator-hub",
    expires: new Date(0),
  });

  redirect("/creator-hub");
}
