import { neon, neonConfig } from "@neondatabase/serverless";
import { drizzle } from "drizzle-orm/neon-http";
import * as schema from "./schema";
import "dotenv/config";

// Configure Neon for serverless
neonConfig.fetchConnectionCache = true;

const databaseUrl = process.env.DATABASE_URL;

if (!databaseUrl) {
  throw new Error("DATABASE_URL environment variable is required");
}

// Create Neon SQL client
const sql = neon(databaseUrl);

// Create Drizzle ORM instance
export const db = drizzle(sql, { schema });

// Export raw SQL client for direct queries
export { sql };
