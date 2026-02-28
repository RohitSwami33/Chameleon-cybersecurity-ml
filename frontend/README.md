# Chameleon Forensics - Frontend

This is the frontend application for Chameleon Forensics, a cutting-edge cybersecurity monitoring and honeypot dashboard, built using modern web development practices and rich 3D visualization tools.

## Tech Stack & Libraries Used

The project is bootstrapped and bundled using [Vite](https://vitejs.dev/) and is entirely written as a [React.js](https://react.dev/) Single Page Application. 

### Core Libraries
- **React (v19) & React DOM (v19)** - Core UI framework.
- **React Router DOM (v7)** - For handling client-side routing.
- **Zustand** - Lightweight and fast global state management.
- **Axios** - For making HTTP requests to the backend logic.

### UI & Styling
- **Material-UI (@mui/material, @mui/icons-material)** - Core component scaling (inputs, buttons, themes).
- **Framer Motion** - Robust animation and gesture library used for page transitions and micro-interactions.
- **Emotion (@emotion/react, @emotion/styled)** - CSS-in-JS used by MUI.
- **React Toastify** - For on-screen notification flashes.
- **Kbar** - Command (+K) bar utility interface to navigate quickly without mouse.

### Data Visualization & 3D
- **Three.js** - Driving custom 3D web graphics.
- **Globe.gl** - WebGL spherical data visualizations (for the real-time Attack Globe).
- **Chart.js & React-Chartjs-2** - For detailed attack metrics line/bar charts.
- **Recharts** - Composable charting library for dashboard components.
- **Spline (@splinetool/react-spline)** - Used to embed real-time 3D assets easily (e.g., glowing AI orbs, interactive backgrounds).

### Utilities
- **Date-fns** - Lightweight date manipulation library for timestamp formatting and comparisons.

---

## Project Structure

```text
frontend/
├── src/
│   ├── assets/              # Static assets (images, SVGs)
│   ├── components/          # Reusable UI components (see below)
│   ├── config/              # Constants and configuration parameters
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Shared libraries and utilities
│   ├── pages/               # Top-level Page components matching routes
│   ├── services/            # API wrappers/HTTP endpoints 
│   ├── stores/              # Zustand global state stores
│   ├── utils/               # Formatting, parsing and generic logic  
│   ├── App.jsx              # Application router & theme setup
│   └── main.jsx             # React entry point
└── package.json             # Manifest and commands
```

---

## Directory of Components

### Pages (`src/pages/`)
- `AnalyticsPage.jsx` - In-depth statistical view of logged incidents.
- `AttackGlobePage.jsx` - A dedicated view highlighting the 3D Globe representation of traffic.
- `ChatbotPage.jsx` - Security assistant conversation interface.
- `DashboardOverview.jsx` - The main mission control page overview.
- `ThreatIntelPage.jsx` - Feed of security threats and intelligence.

### Components (`src/components/`)
A heavily componentized structure for maximum reusability. Key components include:

**Core Dashboards Elements**
- `Dashboard.jsx`, `AttackChart.jsx`, `AttackLogs.jsx`, `ThreatIntelFeed.jsx`, `StatsCards.jsx`, `ThreatScorePanel.jsx`, `Navbar.jsx`

**Map & Global Visualizations**
- `AttackGlobeSimple.jsx`, `WorldMap.jsx`, `GeoMap.jsx`, `AttackTerrainMap.jsx`

**Data Authentication & Access**
- `Login.jsx`, `ProtectedRoute.jsx`

**Decoy/Honeypot Systems**
- `TrapInterface.jsx` - Isolated, multi-stage honeypot UI deliberately structured to distract potential intruders while natively collecting fingerprints.

**App UI & Effects**
- `AIChatbot.jsx`
- `PageTransition.jsx`
- `DepthLayers.jsx`, `GlobalBackground.jsx`, `GlobalGridBackground.jsx` - Decorative background and particle effects.
- `TiltCard.jsx` - Hover 3D interactive layout cards.
- `ui/CommandBar.jsx` - The KBar universal command palette component.
- `ui/FilterBadges.jsx`, `ui/HelpModal.jsx`

**3D Integrations (Three.js/Spline)**
- `AIOrb3D.jsx`
- `BlockchainViz3D.jsx`
- `LoginBackground3D.jsx`, `LoginShield3D.jsx`
- `MerkleTree3D.jsx`
- `ServerRack3D.jsx`
- `ThreatRadar3D.jsx`

**Blockchain Features**
- `BlockchainExplorer.jsx`

---

## Setup & Running Locally

1. Install Dependencies:
   ```bash
   npm install
   ```

2. Start the Development Server:
   ```bash
   npm run dev
   ```

3. Build for Production:
   ```bash
   npm run build
   ```
