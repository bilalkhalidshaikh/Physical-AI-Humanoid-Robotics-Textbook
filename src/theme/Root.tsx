import React from "react";
import { AuthProvider } from "../context/AuthContext";
import { ChatProvider } from "../context/ChatContext";
import AuthModal from "../components/AuthModal";
import OnboardingForm from "../components/OnboardingForm";
import ChatWidget from "../components/ChatWidget";
import TextSelectionHandler from "../components/TextSelectionHandler";

// Swizzled Root component to add global providers and widgets
export default function Root({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <ChatProvider>
        {children}
        {/* Global components */}
        <AuthModal />
        <OnboardingForm />
        <ChatWidget />
        <TextSelectionHandler />
      </ChatProvider>
    </AuthProvider>
  );
}
