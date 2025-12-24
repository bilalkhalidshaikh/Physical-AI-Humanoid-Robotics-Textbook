import { Hono } from "hono";
import { cors } from "hono/cors";
import { logger } from "hono/logger";
import { serve } from "@hono/node-server";
import { auth } from "./auth";
import profileRoutes from "./routes/profile";
import "dotenv/config";

const app = new Hono();

// Middleware
app.use("*", logger());
app.use(
  "*",
  cors({
    origin: process.env.FRONTEND_URL || "http://localhost:3000",
    credentials: true,
    allowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allowHeaders: ["Content-Type", "Authorization"],
  })
);

// Health check endpoint
app.get("/health", (c) => {
  return c.json({
    status: "healthy",
    timestamp: new Date().toISOString(),
    service: "auth-server",
  });
});

// BetterAuth routes - handles /api/auth/*
app.on(["POST", "GET"], "/api/auth/**", (c) => auth.handler(c.req.raw));

// Profile routes
app.route("/api/user", profileRoutes);

// Error handler
app.onError((err, c) => {
  console.error("Server error:", err);
  return c.json(
    {
      error: "Internal server error",
      message: err.message,
    },
    500
  );
});

// 404 handler
app.notFound((c) => {
  return c.json({ error: "Not found" }, 404);
});

const port = parseInt(process.env.PORT || "3001", 10);

console.log(`🚀 Auth server starting on port ${port}`);
console.log(`📍 Frontend URL: ${process.env.FRONTEND_URL || "http://localhost:3000"}`);

serve({
  fetch: app.fetch,
  port,
});

export default app;
