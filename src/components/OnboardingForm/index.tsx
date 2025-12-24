import React, { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import styles from "./styles.module.css";

export default function OnboardingForm() {
  const {
    showOnboarding,
    setShowOnboarding,
    updateProfile,
    completeOnboarding,
  } = useAuth();

  const [softwareBackground, setSoftwareBackground] = useState("");
  const [hardwareBackground, setHardwareBackground] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!showOnboarding) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      // Save profile
      await updateProfile({
        softwareBackground,
        hardwareBackground,
      });

      // Mark onboarding complete
      await completeOnboarding();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save profile");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSkip = async () => {
    setIsLoading(true);
    try {
      await completeOnboarding();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to skip onboarding");
      setIsLoading(false);
    }
  };

  const combinedLength =
    softwareBackground.length + hardwareBackground.length;
  const isOverLimit = combinedLength > 5000;

  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        <h2 className={styles.title}>Welcome! Tell us about yourself</h2>
        <p className={styles.subtitle}>
          Help us personalize your learning experience by sharing your
          background. This helps our AI tailor explanations to your experience
          level.
        </p>

        {error && <div className={styles.error}>{error}</div>}

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label htmlFor="software">Software Background</label>
            <textarea
              id="software"
              value={softwareBackground}
              onChange={(e) => setSoftwareBackground(e.target.value)}
              placeholder="e.g., 3 years Python experience, familiar with ROS, some machine learning..."
              rows={3}
            />
            <span className={styles.hint}>
              Programming languages, frameworks, and tools you've worked with
            </span>
          </div>

          <div className={styles.field}>
            <label htmlFor="hardware">Hardware & Robotics Background</label>
            <textarea
              id="hardware"
              value={hardwareBackground}
              onChange={(e) => setHardwareBackground(e.target.value)}
              placeholder="e.g., Built Arduino projects, some experience with motors and sensors..."
              rows={3}
            />
            <span className={styles.hint}>
              Any robotics, electronics, or mechanical experience
            </span>
          </div>

          {isOverLimit && (
            <div className={styles.warning}>
              Combined text is too long ({combinedLength}/5000 characters)
            </div>
          )}

          <div className={styles.characterCount}>
            {combinedLength}/5000 characters
          </div>

          <div className={styles.actions}>
            <button
              type="button"
              className={styles.skipButton}
              onClick={handleSkip}
              disabled={isLoading}
            >
              Skip for now
            </button>
            <button
              type="submit"
              className={styles.submitButton}
              disabled={isLoading || isOverLimit}
            >
              {isLoading ? "Saving..." : "Save & Continue"}
            </button>
          </div>
        </form>

        <p className={styles.privacy}>
          Your information is only used to personalize content and is never
          shared. You can update this anytime in your profile settings.
        </p>
      </div>
    </div>
  );
}
