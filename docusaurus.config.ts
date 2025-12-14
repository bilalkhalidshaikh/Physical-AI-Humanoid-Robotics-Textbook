import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'A comprehensive textbook on building intelligent humanoid robots',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  // GitHub Pages deployment configuration
  url: 'https://bilalkhalidshaikh.github.io',
  baseUrl: '/Physical-AI-Humanoid-Robotics-Textbook/',
  organizationName: 'bilalkhalidshaikh',
  projectName: 'Physical-AI-Humanoid-Robotics-Textbook',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  // Strict link validation
  onBrokenLinks: 'throw',

  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'throw',
    },
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: '/', // Docs served from root URL
          editUrl: 'https://github.com/bilalkhalidshaikh/Physical-AI-Book/edit/main/',
        },
        blog: false, // Disable blog
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/social-card.jpg',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Physical AI & Humanoid Robotics',
      logo: {
        alt: 'Physical AI Book Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Textbook',
        },
        {
          href: 'https://github.com/bilalkhalidshaikh/Physical-AI-Book',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Modules',
          items: [
            {
              label: 'Module 1: ROS 2',
              to: '/module-1-ros2',
            },
            {
              label: 'Module 2: Digital Twin',
              to: '/module-2-digital-twin',
            },
            {
              label: 'Module 3: AI-Robot Brain',
              to: '/module-3-brain',
            },
            {
              label: 'Module 4: VLA',
              to: '/module-4-vla',
            },
          ],
        },
        {
          title: 'Technologies',
          items: [
            {
              label: 'ROS 2',
              href: 'https://docs.ros.org/en/humble/',
            },
            {
              label: 'Gazebo',
              href: 'https://gazebosim.org/',
            },
            {
              label: 'NVIDIA Isaac Sim',
              href: 'https://developer.nvidia.com/isaac-sim',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/bilalkhalidshaikh/Physical-AI-Book',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics Textbook. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'bash', 'yaml', 'json'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
