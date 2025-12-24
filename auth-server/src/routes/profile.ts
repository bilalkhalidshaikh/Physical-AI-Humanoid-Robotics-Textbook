import { Hono } from "hono";
import { db } from "../db/client";
import { userProfiles, users } from "../db/schema";
import { eq } from "drizzle-orm";
import { auth } from "../auth";

const profileRoutes = new Hono();

// Middleware to verify session
async function getSession(req: Request) {
  const session = await auth.api.getSession({ headers: req.headers });
  return session;
}

// GET /api/user/profile - Get current user's profile
profileRoutes.get("/profile", async (c) => {
  const session = await getSession(c.req.raw);

  if (!session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  const profile = await db.query.userProfiles.findFirst({
    where: eq(userProfiles.userId, session.user.id),
  });

  if (!profile) {
    // Return empty profile if not created yet
    return c.json({
      userId: session.user.id,
      softwareBackground: null,
      hardwareBackground: null,
      backgroundSummary: null,
      preferredLanguage: "en",
      personalizationEnabled: true,
      onboardingCompleted: false,
    });
  }

  return c.json(profile);
});

// POST /api/user/profile - Create or update user profile
profileRoutes.post("/profile", async (c) => {
  const session = await getSession(c.req.raw);

  if (!session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  const body = await c.req.json();
  const {
    softwareBackground,
    hardwareBackground,
    preferredLanguage,
    personalizationEnabled,
  } = body;

  // Validate input
  if (
    preferredLanguage &&
    !["en", "ur"].includes(preferredLanguage)
  ) {
    return c.json({ error: "Invalid language. Must be 'en' or 'ur'" }, 400);
  }

  // Check combined background length
  const combinedLength =
    (softwareBackground?.length || 0) + (hardwareBackground?.length || 0);
  if (combinedLength > 5000) {
    return c.json(
      { error: "Combined background text must be under 5000 characters" },
      400
    );
  }

  // Check if profile exists
  const existingProfile = await db.query.userProfiles.findFirst({
    where: eq(userProfiles.userId, session.user.id),
  });

  const now = new Date();
  const profileData = {
    softwareBackground: softwareBackground || null,
    hardwareBackground: hardwareBackground || null,
    preferredLanguage: preferredLanguage || "en",
    personalizationEnabled:
      personalizationEnabled !== undefined ? personalizationEnabled : true,
    updatedAt: now,
  };

  if (existingProfile) {
    // Update existing profile
    const [updated] = await db
      .update(userProfiles)
      .set(profileData)
      .where(eq(userProfiles.userId, session.user.id))
      .returning();

    return c.json(updated);
  } else {
    // Create new profile
    const [created] = await db
      .insert(userProfiles)
      .values({
        userId: session.user.id,
        ...profileData,
        createdAt: now,
      })
      .returning();

    return c.json(created, 201);
  }
});

// POST /api/user/profile/complete-onboarding - Mark onboarding as complete
profileRoutes.post("/profile/complete-onboarding", async (c) => {
  const session = await getSession(c.req.raw);

  if (!session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  const existingProfile = await db.query.userProfiles.findFirst({
    where: eq(userProfiles.userId, session.user.id),
  });

  const now = new Date();

  if (existingProfile) {
    const [updated] = await db
      .update(userProfiles)
      .set({
        onboardingCompleted: true,
        onboardingCompletedAt: now,
        updatedAt: now,
      })
      .where(eq(userProfiles.userId, session.user.id))
      .returning();

    return c.json(updated);
  } else {
    // Create profile with onboarding completed
    const [created] = await db
      .insert(userProfiles)
      .values({
        userId: session.user.id,
        onboardingCompleted: true,
        onboardingCompletedAt: now,
        createdAt: now,
        updatedAt: now,
      })
      .returning();

    return c.json(created, 201);
  }
});

// DELETE /api/user/profile - Delete user data (FR-033)
profileRoutes.delete("/profile", async (c) => {
  const session = await getSession(c.req.raw);

  if (!session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  // Delete profile (user deletion will cascade)
  await db
    .delete(userProfiles)
    .where(eq(userProfiles.userId, session.user.id));

  return c.json({ success: true, message: "Profile deleted" });
});

export default profileRoutes;
