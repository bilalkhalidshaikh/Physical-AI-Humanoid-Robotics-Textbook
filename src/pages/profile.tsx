import React, { useState, useEffect } from "react";
import Layout from "@theme/Layout";
import { useAuth } from "../context/AuthContext";

export default function ProfilePage() {
  const {
    user,
    profile,
    isAuthenticated,
    isLoading,
    updateProfile,
    logout,
    setShowAuthModal,
  } = useAuth();

  const [softwareBackground, setSoftwareBackground] = useState("");
  const [hardwareBackground, setHardwareBackground] = useState("");
  const [preferredLanguage, setPreferredLanguage] = useState("en");
  const [personalizationEnabled, setPersonalizationEnabled] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  // Load profile data
  useEffect(() => {
    if (profile) {
      setSoftwareBackground(profile.softwareBackground || "");
      setHardwareBackground(profile.hardwareBackground || "");
      setPreferredLanguage(profile.preferredLanguage || "en");
      setPersonalizationEnabled(profile.personalizationEnabled);
    }
  }, [profile]);

  const handleSave = async () => {
    setIsSaving(true);
    setSaveMessage(null);

    try {
      await updateProfile({
        softwareBackground,
        hardwareBackground,
        preferredLanguage: preferredLanguage as "en" | "ur",
        personalizationEnabled,
      });
      setSaveMessage("Profile saved successfully!");
    } catch (err) {
      setSaveMessage("Failed to save profile. Please try again.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    window.location.href = "/";
  };

  if (isLoading) {
    return (
      <Layout title="Profile">
        <div className="container margin-vert--lg">
          <p>Loading...</p>
        </div>
      </Layout>
    );
  }

  if (!isAuthenticated) {
    return (
      <Layout title="Profile">
        <div className="container margin-vert--lg">
          <div className="text--center">
            <h1>Profile</h1>
            <p>Please sign in to view your profile.</p>
            <button
              className="button button--primary button--lg"
              onClick={() => setShowAuthModal(true)}
            >
              Sign In
            </button>
          </div>
        </div>
      </Layout>
    );
  }

  const combinedLength = softwareBackground.length + hardwareBackground.length;

  return (
    <Layout title="Profile">
      <div className="container margin-vert--lg">
        <div className="row">
          <div className="col col--8 col--offset-2">
            <h1>Profile Settings</h1>

            {/* User Info */}
            <div className="card margin-bottom--lg">
              <div className="card__header">
                <h3>Account Information</h3>
              </div>
              <div className="card__body">
                <div style={{ display: "flex", alignItems: "center", gap: "1.5rem", marginBottom: "1rem" }}>
                  {/* Avatar */}
                  {user?.image ? (
                    <img
                      src={user.image}
                      alt={user.name || "User avatar"}
                      style={{
                        width: "80px",
                        height: "80px",
                        borderRadius: "50%",
                        objectFit: "cover",
                      }}
                    />
                  ) : (
                    <div
                      style={{
                        width: "80px",
                        height: "80px",
                        borderRadius: "50%",
                        backgroundColor: "var(--ifm-color-primary)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: "2rem",
                        color: "white",
                        fontWeight: "bold",
                      }}
                    >
                      {(user?.name || user?.email || "U")[0].toUpperCase()}
                    </div>
                  )}
                  <div>
                    {user?.name && (
                      <h4 style={{ margin: 0 }}>{user.name}</h4>
                    )}
                    <p style={{ margin: 0, color: "var(--ifm-color-emphasis-600)" }}>
                      {user?.email}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Background */}
            <div className="card margin-bottom--lg">
              <div className="card__header">
                <h3>Learning Background</h3>
                <p className="margin-bottom--none" style={{ fontSize: "0.9rem", color: "var(--ifm-color-emphasis-600)" }}>
                  This helps our AI personalize content for your experience level.
                </p>
              </div>
              <div className="card__body">
                <div className="margin-bottom--md">
                  <label htmlFor="software" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 600 }}>
                    Software Background
                  </label>
                  <textarea
                    id="software"
                    className="input"
                    value={softwareBackground}
                    onChange={(e) => setSoftwareBackground(e.target.value)}
                    placeholder="e.g., 3 years Python, familiar with ROS..."
                    rows={3}
                    style={{ width: "100%", padding: "0.75rem" }}
                  />
                </div>

                <div className="margin-bottom--md">
                  <label htmlFor="hardware" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 600 }}>
                    Hardware & Robotics Background
                  </label>
                  <textarea
                    id="hardware"
                    className="input"
                    value={hardwareBackground}
                    onChange={(e) => setHardwareBackground(e.target.value)}
                    placeholder="e.g., Arduino projects, motor control..."
                    rows={3}
                    style={{ width: "100%", padding: "0.75rem" }}
                  />
                </div>

                <p style={{ fontSize: "0.85rem", color: "var(--ifm-color-emphasis-600)" }}>
                  {combinedLength}/5000 characters
                </p>
              </div>
            </div>

            {/* Preferences */}
            <div className="card margin-bottom--lg">
              <div className="card__header">
                <h3>Preferences</h3>
              </div>
              <div className="card__body">
                <div className="margin-bottom--md">
                  <label htmlFor="language" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 600 }}>
                    Preferred Language
                  </label>
                  <select
                    id="language"
                    value={preferredLanguage}
                    onChange={(e) => setPreferredLanguage(e.target.value)}
                    style={{ padding: "0.5rem", fontSize: "1rem" }}
                  >
                    <option value="en">English</option>
                    <option value="ur">اردو (Urdu)</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", cursor: "pointer" }}>
                    <input
                      type="checkbox"
                      checked={personalizationEnabled}
                      onChange={(e) => setPersonalizationEnabled(e.target.checked)}
                    />
                    <span>Enable content personalization</span>
                  </label>
                </div>
              </div>
            </div>

            {/* Save Button */}
            <div className="margin-bottom--lg">
              <button
                className="button button--primary button--lg"
                onClick={handleSave}
                disabled={isSaving || combinedLength > 5000}
              >
                {isSaving ? "Saving..." : "Save Changes"}
              </button>

              {saveMessage && (
                <p
                  style={{
                    marginTop: "1rem",
                    color: saveMessage.includes("success")
                      ? "var(--ifm-color-success)"
                      : "var(--ifm-color-danger)",
                  }}
                >
                  {saveMessage}
                </p>
              )}
            </div>

            {/* Danger Zone */}
            <div className="card" style={{ borderColor: "var(--ifm-color-danger)" }}>
              <div className="card__header">
                <h3 style={{ color: "var(--ifm-color-danger)" }}>Account Actions</h3>
              </div>
              <div className="card__body">
                <button
                  className="button button--outline button--danger"
                  onClick={handleLogout}
                >
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
