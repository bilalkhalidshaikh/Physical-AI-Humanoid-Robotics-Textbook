import React, { useEffect } from "react";
import Layout from "@theme/Layout";
import { useAuth } from "../../context/AuthContext";

export default function AuthCallback() {
  const { refreshSession } = useAuth();

  useEffect(() => {
    // Refresh session after OAuth callback
    refreshSession().then(() => {
      // Redirect to home page
      window.location.href = "/";
    });
  }, [refreshSession]);

  return (
    <Layout title="Signing in...">
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "50vh",
          gap: "1rem",
        }}
      >
        <div
          style={{
            width: "40px",
            height: "40px",
            border: "4px solid var(--ifm-color-emphasis-200)",
            borderTopColor: "var(--ifm-color-primary)",
            borderRadius: "50%",
            animation: "spin 0.8s linear infinite",
          }}
        />
        <p style={{ color: "var(--ifm-color-emphasis-600)" }}>
          Completing sign in...
        </p>
        <style>{`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    </Layout>
  );
}
