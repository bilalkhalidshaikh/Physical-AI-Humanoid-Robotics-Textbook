import { createAuthClient } from "better-auth/react";

// const authServerUrl = process.env.REACT_APP_AUTH_SERVER_URL || "http://localhost:3001";
const authServerUrl = "https://bilalanjum-physical-ai-auth.hf.space";

export const authClient = createAuthClient({
  baseURL: authServerUrl,
  credentials: "include",
});

export const {
  signIn,
  signUp,
  signOut,
  useSession,
  getSession,
} = authClient;

// Social login helpers
export async function signInWithGitHub() {
  return authClient.signIn.social({
    provider: "github",
    callbackURL: window.location.origin + "/auth/callback",
  });
}

export async function signInWithGoogle() {
  return authClient.signIn.social({
    provider: "google",
    callbackURL: window.location.origin + "/auth/callback",
  });
}

// Email/password helpers
export async function signInWithEmail(email: string, password: string) {
  return authClient.signIn.email({
    email,
    password,
  });
}

export async function signUpWithEmail(
  email: string,
  password: string,
  name?: string
) {
  return authClient.signUp.email({
    email,
    password,
    name: name || "",
  });
}

// Session helpers
export async function getCurrentSession() {
  try {
    const session = await authClient.getSession();
    return session.data;
  } catch {
    return null;
  }
}

export async function logout() {
  return authClient.signOut();
}

// Types
export type AuthSession = Awaited<ReturnType<typeof getCurrentSession>>;
export type AuthUser = NonNullable<AuthSession>["user"];
