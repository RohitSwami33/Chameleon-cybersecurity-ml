# Chameleon Frontend Walkthrough

I have successfully created the Chameleon Frontend using React and Vite.

## Changes Implemented

### Project Structure
- Initialized a new Vite React project in `frontend/`.
- Configured `.env` with API endpoints.

### Core Infrastructure
- **`src/services/api.js`**: Implemented Axios service for communicating with the backend.
- **`src/utils/helpers.js`**: Added utility functions for formatting, colors, and PDF downloads.
- **`src/App.jsx`**: Set up routing (`/` and `/dashboard`) and Material-UI Dark Theme.
- **`src/App.css` & `src/index.css`**: Added global styles and animations.

### Components
- **`TrapInterface.jsx`**: A realistic-looking fake Admin Portal that acts as the honeypot. It captures user input and sends it to the backend.
- **`Dashboard.jsx`**: The main forensic dashboard. It fetches stats and logs, and includes auto-refresh functionality.
- **`StatsCards.jsx`**: Displays key metrics (Total Attempts, Malicious Attacks, etc.) with visual indicators.
- **`AttackChart.jsx`**: Visualizes attack distribution using Pie and Bar charts (Recharts).
- **`AttackLogs.jsx`**: A detailed table of attack logs with filtering, pagination, and expandable rows showing raw input and deception responses.

## Verification Results

### Build Verification
Ran `npm run build` successfully.
```
vite v7.2.4 building client environment for production...
✓ 1906 modules transformed.                        
dist/index.html                   0.46 kB │ gzip:   0.29 kB
dist/assets/index-D2u_iNUz.css   16.31 kB │ gzip:   3.45 kB
dist/assets/index-CJTrM6BL.js   982.38 kB │ gzip: 304.06 kB
✓ built in 1.61s
```

### Manual Verification Steps
1. **Start the Backend**: Ensure the Chameleon backend is running on port 8000.
2. **Start the Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```
3. **Access the Trap**: Open `http://localhost:5173/` to see the Fake Admin Portal.
4. **Test the Trap**: Try logging in with SQL injection (e.g., `' OR '1'='1`) to trigger the deception engine.
5. **Access the Dashboard**: Open `http://localhost:5173/dashboard` to view the forensics.
6. **Verify Features**:
   - Check if the attack you just performed appears in the logs.
   - Verify the charts update.
   - Try generating a report for an IP.
