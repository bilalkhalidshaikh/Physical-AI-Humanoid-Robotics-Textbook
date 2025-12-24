import {
  pgTable,
  uuid,
  text,
  boolean,
  timestamp,
  integer,
  jsonb,
  unique,
  index,
} from "drizzle-orm/pg-core";

// Users table (BetterAuth compatible - uses camelCase column names)
export const users = pgTable(
  "users",
  {
    id: text("id").primaryKey(), // BetterAuth generates nanoid strings
    email: text("email").notNull().unique(),
    name: text("name"),
    emailVerified: boolean("emailVerified").default(false),
    image: text("image"),
    createdAt: timestamp("createdAt", { withTimezone: true })
      .defaultNow()
      .notNull(),
    updatedAt: timestamp("updatedAt", { withTimezone: true })
      .defaultNow()
      .notNull(),
  },
  (table) => ({
    emailIdx: index("idx_users_email").on(table.email),
  })
);

// User profiles for personalization
export const userProfiles = pgTable("user_profiles", {
  id: uuid("id").primaryKey().defaultRandom(),
  userId: text("user_id") // References text ID from users table
    .notNull()
    .unique()
    .references(() => users.id, { onDelete: "cascade" }),
  softwareBackground: text("software_background"),
  hardwareBackground: text("hardware_background"),
  backgroundSummary: text("background_summary"),
  preferredLanguage: text("preferred_language").default("en"),
  personalizationEnabled: boolean("personalization_enabled").default(true),
  onboardingCompleted: boolean("onboarding_completed").default(false),
  onboardingCompletedAt: timestamp("onboarding_completed_at", {
    withTimezone: true,
  }),
  createdAt: timestamp("created_at", { withTimezone: true })
    .defaultNow()
    .notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true })
    .defaultNow()
    .notNull(),
});

// Sessions table (BetterAuth compatible - uses camelCase column names)
export const sessions = pgTable(
  "sessions",
  {
    id: text("id").primaryKey(), // BetterAuth generates nanoid strings
    userId: text("userId") // BetterAuth expects camelCase column name
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    token: text("token").notNull().unique(),
    expiresAt: timestamp("expiresAt", { withTimezone: true }).notNull(),
    ipAddress: text("ipAddress"),
    userAgent: text("userAgent"),
    createdAt: timestamp("createdAt", { withTimezone: true })
      .defaultNow()
      .notNull(),
    updatedAt: timestamp("updatedAt", { withTimezone: true })
      .defaultNow()
      .notNull(),
  },
  (table) => ({
    userIdIdx: index("idx_sessions_user_id").on(table.userId),
    tokenIdx: index("idx_sessions_token").on(table.token),
    expiresIdx: index("idx_sessions_expires").on(table.expiresAt),
  })
);

// OAuth accounts table (BetterAuth compatible - uses camelCase column names)
export const accounts = pgTable(
  "accounts",
  {
    id: text("id").primaryKey(), // BetterAuth generates nanoid strings
    userId: text("userId") // BetterAuth expects camelCase column name
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    providerId: text("providerId").notNull(),
    accountId: text("accountId").notNull(), // BetterAuth expects accountId
    accessToken: text("accessToken"),
    refreshToken: text("refreshToken"),
    accessTokenExpiresAt: timestamp("accessTokenExpiresAt", { withTimezone: true }),
    refreshTokenExpiresAt: timestamp("refreshTokenExpiresAt", { withTimezone: true }),
    scope: text("scope"),
    idToken: text("idToken"),
    password: text("password"), // For email/password auth
    createdAt: timestamp("createdAt", { withTimezone: true })
      .defaultNow()
      .notNull(),
    updatedAt: timestamp("updatedAt", { withTimezone: true })
      .defaultNow()
      .notNull(),
  },
  (table) => ({
    userIdIdx: index("idx_accounts_user_id").on(table.userId),
    providerIdx: index("idx_accounts_provider").on(
      table.providerId,
      table.accountId
    ),
    providerUnique: unique().on(table.providerId, table.accountId),
  })
);

// Verification table (BetterAuth required - uses camelCase column names)
export const verification = pgTable(
  "verification",
  {
    id: text("id").primaryKey(), // BetterAuth generates nanoid strings
    identifier: text("identifier").notNull(),
    value: text("value").notNull(),
    expiresAt: timestamp("expiresAt", { withTimezone: true }).notNull(),
    createdAt: timestamp("createdAt", { withTimezone: true })
      .defaultNow()
      .notNull(),
    updatedAt: timestamp("updatedAt", { withTimezone: true })
      .defaultNow()
      .notNull(),
  },
  (table) => ({
    identifierIdx: index("idx_verification_identifier").on(table.identifier),
  })
);

// Chat sessions table (app-managed, uses UUID)
export const chatSessions = pgTable(
  "chat_sessions",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    userId: text("user_id").references(() => users.id, { onDelete: "cascade" }), // References text ID
    title: text("title"),
    contextType: text("context_type").default("general"),
    contextSource: text("context_source"),
    contextMetadata: jsonb("context_metadata").default({}),
    isActive: boolean("is_active").default(true),
    messageCount: integer("message_count").default(0),
    createdAt: timestamp("created_at", { withTimezone: true })
      .defaultNow()
      .notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .defaultNow()
      .notNull(),
    lastMessageAt: timestamp("last_message_at", { withTimezone: true }),
  },
  (table) => ({
    userIdIdx: index("idx_chat_sessions_user_id").on(table.userId),
    updatedIdx: index("idx_chat_sessions_updated").on(table.updatedAt),
  })
);

// Chat messages table (app-managed, uses UUID)
export const chatMessages = pgTable(
  "chat_messages",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    sessionId: uuid("session_id")
      .notNull()
      .references(() => chatSessions.id, { onDelete: "cascade" }),
    role: text("role").notNull(),
    content: text("content").notNull(),
    sourceReferences: jsonb("source_references").default([]),
    promptTokens: integer("prompt_tokens"),
    completionTokens: integer("completion_tokens"),
    metadata: jsonb("metadata").default({}),
    createdAt: timestamp("created_at", { withTimezone: true })
      .defaultNow()
      .notNull(),
  },
  (table) => ({
    sessionIdx: index("idx_chat_messages_session").on(table.sessionId),
    createdIdx: index("idx_chat_messages_created").on(
      table.sessionId,
      table.createdAt
    ),
  })
);

// Translation cache table (app-managed, uses UUID)
export const translationCache = pgTable(
  "translation_cache",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    sourcePath: text("source_path").notNull(),
    contentHash: text("content_hash").notNull(),
    targetLanguage: text("target_language").default("ur"),
    translatedContent: text("translated_content").notNull(),
    modelVersion: text("model_version"),
    createdAt: timestamp("created_at", { withTimezone: true })
      .defaultNow()
      .notNull(),
    expiresAt: timestamp("expires_at", { withTimezone: true }),
  },
  (table) => ({
    lookupIdx: index("idx_translation_cache_lookup").on(
      table.sourcePath,
      table.contentHash,
      table.targetLanguage
    ),
    cacheUnique: unique().on(
      table.sourcePath,
      table.contentHash,
      table.targetLanguage
    ),
  })
);

// Personalization cache table (app-managed, uses UUID)
export const personalizationCache = pgTable(
  "personalization_cache",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    userId: text("user_id") // References text ID from users table
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    sourcePath: text("source_path").notNull(),
    contentHash: text("content_hash").notNull(),
    profileHash: text("profile_hash").notNull(),
    personalizedContent: text("personalized_content").notNull(),
    modelVersion: text("model_version"),
    createdAt: timestamp("created_at", { withTimezone: true })
      .defaultNow()
      .notNull(),
  },
  (table) => ({
    lookupIdx: index("idx_personalization_cache_lookup").on(
      table.userId,
      table.sourcePath,
      table.contentHash
    ),
    cacheUnique: unique().on(
      table.userId,
      table.sourcePath,
      table.contentHash,
      table.profileHash
    ),
  })
);

// Type exports
export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;
export type UserProfile = typeof userProfiles.$inferSelect;
export type NewUserProfile = typeof userProfiles.$inferInsert;
export type Session = typeof sessions.$inferSelect;
export type Account = typeof accounts.$inferSelect;
export type ChatSession = typeof chatSessions.$inferSelect;
export type ChatMessage = typeof chatMessages.$inferSelect;
