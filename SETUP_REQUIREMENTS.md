# Chameleon Adaptive Deception System - Setup Requirements

## System Requirements

### Operating System
- **Windows 10/11** (Current deployment)
- Linux (Ubuntu 20.04+) or macOS also supported

### Required Software

#### Python
- **Version**: 3.12.7
- **Download**: https://www.python.org/downloads/

#### Node.js
- **Version**: 18.x or higher (LTS recommended)
- **Download**: https://nodejs.org/

#### MongoDB
- **Version**: 6.0 or higher
- **Options**:
  - Local installation: https://www.mongodb.com/try/download/community
  - MongoDB Atlas (Cloud): https://www.mongodb.com/cloud/atlas

## Backend Setup

### 1. Python Environment

```bash
# Navigate to Backend directory
cd Backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Backend Dependencies

All dependencies are listed in `Backend/requirements.txt` with pinned versions:

#### Core Framework
- `fastapi==0.104.1` - Modern web framework
- `uvicorn==0.24.0` - ASGI server
- `python-multipart==0.0.6` - Form data support

#### Database
- `pymongo==4.6.0` - MongoDB driver
- `motor==3.3.2` - Async MongoDB driver

#### Machine Learning
- `tensorflow==2.16.0` - Attack classification
- `numpy==1.24.3` - Numerical computing

#### Security
- `python-jose[cryptography]==3.3.0` - JWT tokens
- `passlib[bcrypt]==1.7.4` - Password hashing

#### Blockchain
- `web3==6.11.3` - Ethereum integration

#### Other
- `pydantic==2.5.0` - Data validation
- `httpx==0.25.2` - Async HTTP client
- `reportlab==4.0.7` - PDF generation
- `python-dotenv==1.0.0` - Environment config

### 3. Environment Configuration

Create a `.env` file in the `Backend` directory:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=chameleon_db

# JWT Secret (generate a secure random string)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password

# GeoIP API
GEOIP_API_URL=http://ip-api.com/json/

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### 4. Start Backend Server

```bash
# From Backend directory
uvicorn main:app --reload

# Server will start at http://localhost:8000
# API docs available at http://localhost:8000/docs
```

## Frontend Setup

### 1. Install Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install npm packages
npm install
```

### 2. Frontend Dependencies

All dependencies are listed in `frontend/package.json`:

#### Core Framework
- `react==19.2.0` - UI library
- `react-dom==19.2.0` - React DOM renderer
- `react-router-dom==7.9.6` - Routing

#### UI Components
- `@mui/material==7.3.5` - Material-UI components
- `@mui/icons-material==7.3.5` - Material-UI icons
- `@emotion/react==11.14.0` - CSS-in-JS
- `@emotion/styled==11.14.1` - Styled components

#### Data Visualization
- `chart.js==4.5.1` - Chart library
- `react-chartjs-2==5.3.1` - React wrapper for Chart.js
- `recharts==3.4.1` - Alternative charting library
- `globe.gl==2.45.0` - 3D globe visualization
- `three==0.181.2` - 3D graphics library

#### State Management & Utilities
- `zustand==5.0.8` - State management
- `axios==1.13.2` - HTTP client
- `kbar==0.1.0-beta.48` - Command bar
- `react-toastify==11.0.5` - Toast notifications
- `date-fns==4.1.0` - Date utilities

#### Build Tools
- `vite==7.2.4` - Build tool
- `@vitejs/plugin-react==5.1.1` - React plugin for Vite
- `eslint==9.39.1` - Linting

### 3. Environment Configuration

Create a `.env` file in the `frontend` directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 4. Start Frontend Development Server

```bash
# From frontend directory
npm run dev

# Server will start at http://localhost:5173
```

## Database Setup

### MongoDB Local Installation

1. **Install MongoDB Community Edition**
   - Download from: https://www.mongodb.com/try/download/community
   - Follow installation instructions for your OS

2. **Start MongoDB Service**
   ```bash
   # Windows (as Administrator)
   net start MongoDB
   
   # Linux
   sudo systemctl start mongod
   
   # macOS
   brew services start mongodb-community
   ```

3. **Verify Connection**
   ```bash
   mongosh
   # Should connect to mongodb://localhost:27017
   ```

### MongoDB Atlas (Cloud)

1. **Create Account**: https://www.mongodb.com/cloud/atlas
2. **Create Cluster**: Follow the setup wizard
3. **Get Connection String**: 
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string
4. **Update Backend .env**:
   ```env
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
   ```

## Running the Complete System

### Option 1: Manual Start (Development)

```bash
# Terminal 1 - Backend
cd Backend
venv\Scripts\activate  # Windows
uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Option 2: Quick Start Script (Windows)

Create `start.bat`:
```batch
@echo off
echo Starting Chameleon System...

start cmd /k "cd Backend && venv\Scripts\activate && uvicorn main:app --reload"
start cmd /k "cd frontend && npm run dev"

echo System started!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
```

## Verification

### Backend Health Check
```bash
curl http://localhost:8000/api/health
# Should return: {"status":"healthy","timestamp":"..."}
```

### Frontend Access
1. Open browser: http://localhost:5173
2. Login page should appear
3. Default credentials: admin / your-secure-password

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Backend Issues

**MongoDB Connection Error**
```
Solution: Ensure MongoDB is running and connection string is correct
Check: mongosh to verify MongoDB is accessible
```

**TensorFlow Loading Error**
```
Solution: TensorFlow model may be missing or corrupted
The system will fall back to heuristic-based classification
```

**Port Already in Use**
```
Solution: Change port in .env or kill process using the port
Windows: netstat -ano | findstr :8000
Linux: lsof -i :8000
```

### Frontend Issues

**Module Not Found**
```
Solution: Delete node_modules and package-lock.json, then npm install
```

**API Connection Error**
```
Solution: Verify VITE_API_BASE_URL in .env matches backend URL
Check: Backend is running and accessible
```

**Build Errors**
```
Solution: Clear Vite cache
npm run build -- --force
```

## Production Deployment

### Backend
```bash
# Install production dependencies
pip install -r requirements.txt

# Run with production server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend
```bash
# Build for production
npm run build

# Serve with nginx, Apache, or any static file server
# Build output is in: frontend/dist/
```

## Version History

- **Python**: 3.12.7
- **Node.js**: 18.x+
- **MongoDB**: 6.0+
- **Last Updated**: 2025-11-23

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API documentation at /docs
3. Check system logs in Backend/backend.log
4. Verify all environment variables are set correctly

## Security Notes

⚠️ **Important for Production**:
1. Change default admin password
2. Use strong SECRET_KEY (generate with: `openssl rand -hex 32`)
3. Enable HTTPS/TLS
4. Configure CORS properly in main.py
5. Use MongoDB authentication
6. Keep dependencies updated
7. Review security best practices in documentation
