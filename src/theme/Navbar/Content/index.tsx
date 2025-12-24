import React from "react";
import { useThemeConfig, ErrorCauseBoundary } from "@docusaurus/theme-common";
import {
  splitNavbarItems,
  useNavbarMobileSidebar,
} from "@docusaurus/theme-common/internal";
import NavbarItem from "@theme/NavbarItem";
import NavbarColorModeToggle from "@theme/Navbar/ColorModeToggle";
import SearchBar from "@theme/SearchBar";
import NavbarMobileSidebarToggle from "@theme/Navbar/MobileSidebar/Toggle";
import NavbarLogo from "@theme/Navbar/Logo";
import NavbarSearch from "@theme/Navbar/Search";
import useBaseUrl from "@docusaurus/useBaseUrl";
import { useAuth } from "../../../context/AuthContext";
import styles from "./styles.module.css";

function useNavbarItems() {
  return useThemeConfig().navbar.items;
}

function NavbarItems({ items }: { items: any[] }) {
  return (
    <>
      {items.map((item, i) => (
        <ErrorCauseBoundary
          key={i}
          onError={(error) =>
            new Error(
              `A theme navbar item failed to render.
Please double-check the following navbar item (themeConfig.navbar.items) of your Docusaurus config:
${JSON.stringify(item, null, 2)}`,
              { cause: error }
            )
          }
        >
          <NavbarItem {...item} />
        </ErrorCauseBoundary>
      ))}
    </>
  );
}

function NavbarContentLayout({
  left,
  right,
}: {
  left: React.ReactNode;
  right: React.ReactNode;
}) {
  return (
    <div className="navbar__inner">
      <div className="navbar__items">{left}</div>
      <div className="navbar__items navbar__items--right">{right}</div>
    </div>
  );
}

function AuthButton() {
  const { isAuthenticated, user, isLoading, setShowAuthModal, logout } =
    useAuth();
  const profileUrl = useBaseUrl("/profile");

  if (isLoading) {
    return null;
  }

  if (isAuthenticated && user) {
    return (
      <div className={styles.userMenu}>
        <button className={styles.userButton}>
          {user.image ? (
            <img
              src={user.image}
              alt={user.name || "User"}
              className={styles.avatar}
            />
          ) : (
            <span className={styles.avatarPlaceholder}>
              {(user.name || user.email || "U")[0].toUpperCase()}
            </span>
          )}
          <span className={styles.userName}>
            {user.name || user.email?.split("@")[0]}
          </span>
        </button>
        <div className={styles.dropdown}>
          <a href={profileUrl} className={styles.dropdownItem}>
            Profile Settings
          </a>
          <button
            className={styles.dropdownItem}
            onClick={() => logout()}
          >
            Sign Out
          </button>
        </div>
      </div>
    );
  }

  return (
    <button
      className={styles.loginButton}
      onClick={() => setShowAuthModal(true)}
    >
      Sign In
    </button>
  );
}

export default function NavbarContent() {
  const mobileSidebar = useNavbarMobileSidebar();
  const items = useNavbarItems();
  const [leftItems, rightItems] = splitNavbarItems(items);
  const searchBarItem = items.find((item: any) => item.type === "search");

  return (
    <NavbarContentLayout
      left={
        <>
          {!mobileSidebar.disabled && <NavbarMobileSidebarToggle />}
          <NavbarLogo />
          <NavbarItems items={leftItems} />
        </>
      }
      right={
        <>
          <NavbarItems items={rightItems} />
          <NavbarColorModeToggle className={styles.colorModeToggle} />
          {!searchBarItem && (
            <NavbarSearch>
              <SearchBar />
            </NavbarSearch>
          )}
          <AuthButton />
        </>
      }
    />
  );
}
