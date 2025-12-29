import React from "react";
import BrowserOnly from "@docusaurus/BrowserOnly";

// ⚠️ NUCLEAR FIX: We do NOT import Providers or Components at the top.
// This prevents the server from ever seeing the "unsafe" code.

export default function Root({ children }: { children: React.ReactNode }) {
  return (
    <>
      {/* 1. Render the Textbook Content (Safe for Server) */}
      {children}

      {/* 2. Render the AI App (Browser Only) */}
      {/* This ensures Auth/Chat logic ONLY runs on the user's device, never on GitHub's server */}
      <BrowserOnly>
        {() => {
          // Lazy load EVERYTHING here.
          const { AuthProvider } = require("../context/AuthContext");
          const { ChatProvider } = require("../context/ChatContext");
          const AuthModal = require("../components/AuthModal").default;
          const OnboardingForm = require("../components/OnboardingForm").default;
          const ChatWidget = require("../components/ChatWidget").default;
          const TextSelectionHandler = require("../components/TextSelectionHandler").default;

          return (
            <AuthProvider>
              <ChatProvider>
                <AuthModal />
                <OnboardingForm />
                <ChatWidget />
                <TextSelectionHandler />
              </ChatProvider>
            </AuthProvider>
          );
        }}
      </BrowserOnly>
    </>
  );
}