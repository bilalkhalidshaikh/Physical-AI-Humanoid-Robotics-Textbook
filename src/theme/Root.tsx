import React from "react";
import { AuthProvider } from "../context/AuthContext";
import { ChatProvider } from "../context/ChatContext";
import BrowserOnly from "@docusaurus/BrowserOnly";

// Swizzled Root component to add global providers and widgets
export default function Root({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <ChatProvider>
        {children}

        {/* Global interactive components moved inside BrowserOnly for SSR compatibility */}
        <BrowserOnly>
          {() => {
            const AuthModal = require("../components/AuthModal").default;
            const OnboardingForm = require("../components/OnboardingForm").default;
            const ChatWidget = require("../components/ChatWidget").default;
            const TextSelectionHandler = require("../components/TextSelectionHandler").default;

            return (
              <>
                <AuthModal />
                <OnboardingForm />
                <ChatWidget />
                <TextSelectionHandler />
              </>
            );
          }}
        </BrowserOnly>
      </ChatProvider>
    </AuthProvider>
  );
}

