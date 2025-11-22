# 🦎 Chameleon Adaptive Deception System

> An advanced cybersecurity honeypot system with progressive deception, blockchain-based forensic logging, and AI-powered threat detection.

[![Python](https://img.shields.io/badge/Python-3.12.7-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.2.0-blue.svg)](https://reactjs.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-green.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Overview

Chameleon is a next-generation adaptive deception system that creates a "narrative of failure" for attackers while gathering forensic intelligence. It combines machine learning, blockchain technology, and progressive deception techniques to waste attacker time while maintaining immutable evidence logs.

### Key Features

#### 🎭 Progressive Deception Engine V2
- **Stage-Based Responses**: Attackers progress through 4 stages of SQL injection or 3 stages of XSS deception
- **Context-Aware Errors**: Extracts table/column names from payloads for realistic error messages
- **Session Tracking**: Unique fingerprinting per attacker (IP + User-Agent)
- **Database Consistency**: Randomly assigns database type (MySQL, PostgreSQL, SQLite) per session
- **Narrative of Failure**: Creates believable progression that wastes attacker time

#### 🔗 Blockchain Forensic Logging
- **Immutable Evidence**: All attack logs stored in blockchain with SHA-256 hashing
- **Merkle Root Verification**: Cryptographic proof of evidence integrity
- **Tamper Detection**: Detects insider or persistent attacker modifications
- **Chain Integrity**: Real-time verification of blockchain consistency

#### 🤖 AI-Powered Threat Detection
- **ML Classification**: TensorFlow-based attack type detection
- **Threat Scoring**: Dynamic reputation system with blockchain tracking
- **Attack Types**: SQL Injection, XSS, SSI, Brute Force detection
- **Confidence Scoring**: Probabilistic classification with confidence levels

#### 🌍 Real-Time Threat Intelligence
- **3D Attack Globe**: Interactive visualization of global attack origins
- **Geo-Location Tracking**: IP-based geographic attribution
- **Live Dashboard**: Real-time statistics and threat monitoring
- **Command Bar**: Natural language filtering (e.g., "type:sqli from:CN")

#### ⏱️ Adaptive Tarpit
- **Progressive Delays**: Increases response time for repeat offenders
- **IP Blocking**: Automatic blocking after threshold violations
- **Resource Protection**: Prevents DoS while maintaining deception

#### 📊 Comprehensive Analytics
- **Attack Distribution**: Visual breakdown by attack type
- **Top Threats**: Ranked list of most dangerous IPs
- **Session Analytics**: Track attacker progression through deception stages
- **Incident Reports**: PDF generation for forensic analysis

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Dashboard │  │3D Globe  │  │Command   │  │Blockchain│   │
│  │          │  │Visualize │  │Bar       │  │Explorer  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Progressive Deception Engine V2                      │  │
│  │  • Stage-based SQL/XSS responses                      │  │
│  │  • Context extraction from payloads                   │  │
│  │  • Session fingerprinting & tracking                  │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ML Classifier (TensorFlow)                           │  │
│  │  • Attack type detection                              │  │
│  │  • Confidence scoring                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Blockchain Logger                                     │  │
│  │  • SHA-256 hashing                                    │  │
│  │  • Merkle tree construction                           │  │
│  │  • Chain integrity verification                       │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Threat Score System                                   │  │
│  │  • Dynamic reputation tracking                        │  │
│  │  • Blockchain-based score history                     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Adaptive Tarpit                                       │  │
│  │  • Progressive delays                                 │  │
│  │  • IP blocking                                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   MongoDB     │
                    │  • Attack logs│
                    │  • Sessions   │
                    │  • Analytics  │
                    └───────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.12.7**
- **Node.js 18.x+**
- **MongoDB 6.0+**

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/chameleon-deception.git
   cd chameleon-deception
   ```

2. **Backend Setup**
   ```bash
   cd Backend
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

3. **Configure Backend**
   Create `Backend/.env`:
   ```env
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=chameleon_db
   SECRET_KEY=your-secret-key-here
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your-secure-password
   ```

4. **Frontend Setup**
   ```bash
   cd ../frontend
   npm install
   ```

5. **Configure Frontend**
   Create `frontend/.env`:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

6. **Start Services**
   ```bash
   # Terminal 1 - Backend
   cd Backend
   uvicorn main:app --reload

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

7. **Access the System**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

For detailed setup instructions, see [SETUP_REQUIREMENTS.md](SETUP_REQUIREMENTS.md)

## 📖 Usage

### Honeypot Interface

The system provides a fake admin login portal at the root URL that serves as the honeypot trap:

```
http://localhost:5173/trap
```

Attackers interacting with this interface will:
1. Be fingerprinted and tracked
2. Receive progressive deceptive responses
3. Have all actions logged to blockchain
4. Be scored by the threat intelligence system

### Admin Dashboard

Access the forensic dashboard at:

```
http://localhost:5173/login
```

Default credentials: `admin` / `your-secure-password`

#### Dashboard Features

- **Real-time Statistics**: Total attempts, malicious vs benign breakdown
- **3D Attack Globe**: Visual representation of attack origins
- **Attack Distribution**: Charts showing attack types
- **Geographic Origins**: Map of attack source locations
- **Threat Scores**: Top threats and flagged IPs
- **System Health**: Deception engine, blockchain, and tarpit status
- **Merkle Root Display**: Forensic evidence integrity verification
- **Attack Logs**: Detailed log viewer with filtering
- **Command Bar**: Natural language search (Ctrl+K / Cmd+K)

### Command Bar Examples

Press `Ctrl+K` (or `Cmd+K` on Mac) to open the command bar:

```
type:sqli              # Filter SQL injection attacks
from:CN                # Filter attacks from China
ip:192.168.1.1         # Filter specific IP
malicious:true         # Show only malicious attacks
date:today             # Today's attacks
reset                  # Clear all filters
```

### API Endpoints

#### Submit Attack (Honeypot)
```bash
POST /api/trap/submit
{
  "input_text": "' OR '1'='1",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0..."
}
```

#### Get Dashboard Stats
```bash
GET /api/dashboard/stats
Authorization: Bearer <token>
```

#### View Blockchain
```bash
GET /api/blockchain/verify
Authorization: Bearer <token>
```

#### Threat Scores
```bash
GET /api/threat-scores/top-threats?limit=10
Authorization: Bearer <token>
```

Full API documentation: http://localhost:8000/docs

## 🧪 Testing

### Progressive Deception Test

Test the 4-stage SQL injection deception:

```bash
# Stage 1: Syntax Error
curl -X POST http://localhost:8000/api/trap/submit \
  -H "Content-Type: application/json" \
  -d '{"input_text": "admin'\'' OR '\''1'\''='\''1"}'

# Stage 2: Table Not Found
# (repeat same request)

# Stage 3: Column Not Found
# (repeat same request)

# Stage 4: Readonly Database
# (repeat same request - stays here)
```

### Run Test Suite

```bash
# Backend tests
cd Backend
python test_progressive_deception.py

# Frontend tests
cd frontend
npm test
```

## 📊 Progressive Deception Stages

### SQL Injection (4 Stages)

1. **Syntax Error**: Makes attacker fix SQL syntax
   ```
   Error 1064: You have an error in your SQL syntax...
   ```

2. **Table Not Found**: Makes attacker enumerate tables
   ```
   Error 1146: Table 'webapp_db.users' doesn't exist
   ```

3. **Column Not Found**: Makes attacker enumerate columns
   ```
   Error 1054: Unknown column 'password' in 'field list'
   ```

4. **Permission Denied**: Ultimate frustration (final stage)
   ```
   Error: attempt to write a readonly database
   ```

### XSS (3 Stages)

1. **CSP Violation**: Makes attacker try to bypass CSP
2. **Input Sanitization**: Shows characters being stripped
3. **Obfuscation Detection**: Final security alert

## 🔒 Security Features

- **JWT Authentication**: Secure token-based auth for dashboard
- **Password Hashing**: Bcrypt hashing for credentials
- **Rate Limiting**: Brute force protection on login
- **CORS Configuration**: Controlled cross-origin access
- **Input Validation**: Pydantic models for all inputs
- **Blockchain Integrity**: Immutable evidence logging
- **Session Isolation**: Separate deception per attacker

## 📈 Threat Intelligence

### Threat Score Levels

- **TRUSTED** (90-100): Legitimate traffic
- **NEUTRAL** (70-89): Unknown/minimal activity
- **SUSPICIOUS** (40-69): Potential threat
- **MALICIOUS** (10-39): Confirmed attacks
- **CRITICAL** (0-9): Severe threat actor

### Score Calculation

Scores decrease based on:
- Attack type severity (SQLi: -15, XSS: -10, etc.)
- Attack frequency
- Malicious classification confidence

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **TensorFlow** - Machine learning for attack classification
- **MongoDB** - NoSQL database for logs and analytics
- **Web3.py** - Blockchain integration
- **ReportLab** - PDF report generation
- **Python-JOSE** - JWT token handling

### Frontend
- **React 19** - UI library
- **Material-UI** - Component library
- **Globe.gl** - 3D globe visualization
- **Chart.js** - Data visualization
- **Zustand** - State management
- **KBar** - Command bar interface
- **Axios** - HTTP client

### Infrastructure
- **MongoDB** - Database
- **Uvicorn** - ASGI server
- **Vite** - Frontend build tool

## 📝 Documentation

- [Setup Requirements](SETUP_REQUIREMENTS.md) - Detailed installation guide
- [Progressive Deception Fixed](PROGRESSIVE_DECEPTION_FIXED.md) - Deception engine details
- [Dashboard Fixes](DASHBOARD_FIXES_COMPLETE.md) - Dashboard features
- [API Documentation](http://localhost:8000/docs) - Interactive API docs

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- MongoDB for scalable data storage
- TensorFlow for ML capabilities
- The cybersecurity community for inspiration

## 📧 Contact

For questions or support:
- Open an issue on GitHub
- Check the documentation
- Review API docs at `/docs`

## 🔮 Roadmap

- [ ] Advanced ML models for attack prediction
- [ ] Multi-honeypot orchestration
- [ ] Threat intelligence sharing
- [ ] Advanced analytics dashboard
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Integration with SIEM systems
- [ ] Advanced deception techniques

---

**⚠️ Disclaimer**: This system is designed for cybersecurity research and defense. Use responsibly and in accordance with applicable laws and regulations.

**Made with ❤️ for the cybersecurity community**
