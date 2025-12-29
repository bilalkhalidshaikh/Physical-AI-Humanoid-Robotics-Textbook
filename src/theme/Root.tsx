// import React from "react";
// import { AuthProvider } from "../context/AuthContext";
// import { ChatProvider } from "../context/ChatContext";
// import AuthModal from "../components/AuthModal";
// import OnboardingForm from "../components/OnboardingForm";
// import ChatWidget from "../components/ChatWidget";
// import TextSelectionHandler from "../components/TextSelectionHandler";
// import BrowserOnly from "@docusaurus/BrowserOnly"; // 1. Import this

// // Swizzled Root component to add global providers and widgets
// export default function Root({ children }: { children: React.ReactNode }) {
//   return (
//     <AuthProvider>
//       <ChatProvider>
//         {children}
//         {/* Global components */}
//         <AuthModal />
//         <OnboardingForm />
//         {/* <ChatWidget /> */}
//         <BrowserOnly>
//           {() => {
//             const ChatWidget = require("../components/ChatWidget").default; // 2. Lazy load it
//             return <ChatWidget />;
//           }}
//         </BrowserOnly>
//         <TextSelectionHandler />
//       </ChatProvider>
//     </AuthProvider>
//   );
// }









import React from "react";
import { AuthProvider } from "../context/AuthContext";
import { ChatProvider } from "../context/ChatContext";
import BrowserOnly from "@docusaurus/BrowserOnly";

// NOTE: We do NOT import components at the top level to prevent
// "window is not defined" errors during the build.

export default function Root({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <ChatProvider>
        {children}
        <BrowserOnly>
          {() => {
            // Lazy load components only when we are in the browser
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