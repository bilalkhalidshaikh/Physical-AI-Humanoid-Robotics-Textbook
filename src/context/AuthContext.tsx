import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from "react";
import {
  getCurrentSession,
  logout as authLogout,
  type AuthSession,
  type AuthUser,
} from "../lib/auth-client";

interface UserProfile {
  userId: string;
  softwareBackground: string | null;
  hardwareBackground: string | null;
  backgroundSummary: string | null;
  preferredLanguage: "en" | "ur";
  personalizationEnabled: boolean;
  onboardingCompleted: boolean;
}

interface AuthContextValue {
  // State
  user: AuthUser | null;
  session: AuthSession | null;
  profile: UserProfile | null;
  isLoading: boolean;
  isAuthenticated: boolean;

  // Actions
  refreshSession: () => Promise<void>;
  logout: () => Promise<void>;
  fetchProfile: () => Promise<void>;
  updateProfile: (data: Partial<UserProfile>) => Promise<void>;
  completeOnboarding: () => Promise<void>;

  // UI State
  showAuthModal: boolean;
  setShowAuthModal: (show: boolean) => void;
  showOnboarding: boolean;
  setShowOnboarding: (show: boolean) => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// const AUTH_SERVER_URL = process.env.REACT_APP_AUTH_SERVER_URL || "http://localhost:3001";
const AUTH_SERVER_URL = "http://localhost:3001";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<AuthSession | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);

  const user = session?.user ?? null;
  const isAuthenticated = !!user;

  // Fetch user profile from auth server
  const fetchProfile = useCallback(async () => {
    if (!isAuthenticated) {
      setProfile(null);
      return;
    }

    try {
      const response = await fetch(`${AUTH_SERVER_URL}/api/user/profile`, {
        credentials: "include",
      });

      if (response.ok) {
        const data = await response.json();
        setProfile({
          userId: data.user_id || data.userId,
          softwareBackground: data.software_background || data.softwareBackground,
          hardwareBackground: data.hardware_background || data.hardwareBackground,
          backgroundSummary: data.background_summary || data.backgroundSummary,
          preferredLanguage: data.preferred_language || data.preferredLanguage || "en",
          personalizationEnabled: data.personalization_enabled ?? data.personalizationEnabled ?? true,
          onboardingCompleted: data.onboarding_completed ?? data.onboardingCompleted ?? false,
        });
      }
    } catch (error) {
      console.error("Failed to fetch profile:", error);
    }
  }, [isAuthenticated]);

  // Refresh session from auth server
  const refreshSession = useCallback(async () => {
    setIsLoading(true);
    try {
      const currentSession = await getCurrentSession();
      setSession(currentSession);

      if (currentSession?.user) {
        await fetchProfile();
      } else {
        setProfile(null);
      }
    } catch (error) {
      console.error("Failed to refresh session:", error);
      setSession(null);
      setProfile(null);
    } finally {
      setIsLoading(false);
    }
  }, [fetchProfile]);

  // Logout
  const logout = useCallback(async () => {
    try {
      await authLogout();
      setSession(null);
      setProfile(null);
    } catch (error) {
      console.error("Logout failed:", error);
    }
  }, []);

  // Update profile
  const updateProfile = useCallback(
    async (data: Partial<UserProfile>) => {
      if (!isAuthenticated) return;

      try {
        const response = await fetch(`${AUTH_SERVER_URL}/api/user/profile`, {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            softwareBackground: data.softwareBackground,
            hardwareBackground: data.hardwareBackground,
            preferredLanguage: data.preferredLanguage,
            personalizationEnabled: data.personalizationEnabled,
          }),
        });

        if (response.ok) {
          await fetchProfile();
        }
      } catch (error) {
        console.error("Failed to update profile:", error);
        throw error;
      }
    },
    [isAuthenticated, fetchProfile]
  );

  // Complete onboarding
  const completeOnboarding = useCallback(async () => {
    if (!isAuthenticated) return;

    try {
      const response = await fetch(
        `${AUTH_SERVER_URL}/api/user/profile/complete-onboarding`,
        {
          method: "POST",
          credentials: "include",
        }
      );

      if (response.ok) {
        await fetchProfile();
        setShowOnboarding(false);
      }
    } catch (error) {
      console.error("Failed to complete onboarding:", error);
      throw error;
    }
  }, [isAuthenticated, fetchProfile]);

  // Check session on mount
  useEffect(() => {
    refreshSession();
  }, [refreshSession]);

  // Trigger onboarding for new users
  useEffect(() => {
    if (isAuthenticated && profile && !profile.onboardingCompleted) {
      setShowOnboarding(true);
    }
  }, [isAuthenticated, profile]);

  const value: AuthContextValue = {
    user,
    session,
    profile,
    isLoading,
    isAuthenticated,
    refreshSession,
    logout,
    fetchProfile,
    updateProfile,
    completeOnboarding,
    showAuthModal,
    setShowAuthModal,
    showOnboarding,
    setShowOnboarding,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

// Export types
export type { AuthContextValue, UserProfile };
