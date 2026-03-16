# Chameleon — AI-Driven Adaptive Honeypot System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/FastAPI-Latest-green?style=for-the-badge&logo=fastapi" />
  <img src="https://img.shields.io/badge/PyTorch-BiLSTM-red?style=for-the-badge&logo=pytorch" />
  <img src="https://img.shields.io/badge/MLX-Qwen_LLM-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Tests-91%2F91_PASS-brightgreen?style=for-the-badge" />
</p>

> **Chameleon** is an AI-powered honeypot that uses a custom BiLSTM anomaly filter, a locally-running MLX Qwen LLM, and two novel meta-heuristic optimization algorithms — **Threat-Calibrated PSO (TC-PSO)** and **Semantic Deception RRT (S-RRT)** — to dynamically adapt its deception behavior in real time against live attackers.

---

## 📁 Directory Structure

```
Chameleon-cybersecurity-ml/
├── Backend/                   ← FastAPI server root (Render entry point)
│   ├── main.py                ← Server entry point: uvicorn main:app
│   ├── conftest.py            ← pytest fixtures
│   ├── pytest.ini             ← test config
│   │
│   ├── src/                   ← Core source library
│   │   ├── optimization/      ← TC-PSO & S-RRT novel algorithms
│   │   │   └── meta_heuristics.py
│   │   ├── ml_engine/         ← BiLSTM + MLX Qwen inference layer
│   │   │   ├── local_inference.py
│   │   │   ├── bilstm_inference.py
│   │   │   └── ml_classifier.py
│   │   ├── core/              ← Config, Pydantic models, database
│   │   │   ├── config.py, models.py, models_sqlalchemy.py
│   │   │   └── database.py, database_postgres.py
│   │   ├── api/               ← FastAPI routes, pipeline, auth
│   │   │   ├── main.py, pipeline.py, auth.py
│   │   └── utils/             ← Services: tarpit, deception, blockchain, chat
│   │
│   ├── models/                ← Trained model weights (*.keras, *.pth, *.pt)
│   ├── tests/                 ← Novel equation test suite (91 tests)
│   ├── test_results/          ← Pytest outputs & COMPARISON_REPORT.md
│   ├── docs/                  ← Research docs, graphs (*.md, *.png)
│   ├── data/                  ← Training datasets (*.csv, *.jsonl)
│   ├── scripts/               ← Training & seeding scripts
│   ├── migrations/            ← Alembic DB migrations
│   ├── network/               ← SSH honeypot sensor
│   └── sensors/               ← Remote sensor agent
│
├── Frontend/                  ← React dashboard
├── NOVEL_EQUATIONS_DOCUMENTATION.md  ← Research paper
└── README.md                  ← This file
```

---

## 🧠 Architecture Overview

Chameleon operates as a multi-layer honeypot where incoming traffic is first classified by a BiLSTM anomaly scorer producing a score A(t) ∈ [0,1]. This score feeds TC-PSO's dynamic inertia equation `w(t) = w_base · max(σ_min, 1 − α·A(t))` to adaptively tune the tarpit delay, while simultaneously scaling fitness rewards via `F'(t) = F(t)·(1 + β·A(t))`. In parallel, S-RRT evolves a population of deception filesystem schemas using an exponential pheromone update `Δτ' = Δτ·exp(Ψ−1)` driven by LLM-generated payload severity indices (PSI), controlled by a depth-decay expansion rule `P'_expand = P_expand·max(ε, 1 − d/d_max)` that bounds memory growth mathematically. The MLX Qwen LLM generates contextually deceptive responses to sustain attacker engagement.

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
cd Backend
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Fill in: DATABASE_URL, OPENAI_API_KEY or local model path, etc.
```

### 3. Run the server
```bash
cd Backend
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Run the test suite
```bash
cd Backend
python3 -m pytest tests/ -v --asyncio-mode=auto
# Expected: 91/91 PASS
```

---

## 📊 Novel Equations — Benchmark Results

| Metric | Baseline | Novel (Ours) | Δ |
|--------|---------|-------------|---|
| TC-PSO Avg Fitness (100 iters, A=0.85) | 5.19 | **7.30** | **+40.5%** |
| S-RRT Best Fitness (15 gens, PSI=2.8) | ~60,556 | **~411,619** | **+579.7%** |
| S-RRT Memory Growth (25 generations) | Unbounded | **1.00×** | Bounded ✅ |

See [`NOVEL_EQUATIONS_DOCUMENTATION.md`](NOVEL_EQUATIONS_DOCUMENTATION.md) and [`Backend/test_results/COMPARISON_REPORT.md`](Backend/test_results/COMPARISON_REPORT.md) for full details.

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [`NOVEL_EQUATIONS_DOCUMENTATION.md`](NOVEL_EQUATIONS_DOCUMENTATION.md) | Research paper — TC-PSO & S-RRT equations, proofs, benchmarks |
| [`Backend/test_results/COMPARISON_REPORT.md`](Backend/test_results/COMPARISON_REPORT.md) | Algorithm comparison vs PSO, RRT baselines |
| [`Backend/docs/`](Backend/docs/) | Additional research docs & graphs |

---

## 🧪 Test Suite

```
Backend/tests/
├── test_tc_pso_equations.py     # 24 tests — Equations 1 & 2
├── test_s_rrt_equations.py      # 27 tests — Equations 3 & 4
├── test_mathematical_proofs.py  # 31 tests — Convergence & memory proofs
└── test_comparison_algorithms.py #  9 tests — TC-PSO vs PSO, S-RRT vs RRT
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| API Server | FastAPI + Uvicorn |
| Anomaly Detection | PyTorch BiLSTM (custom trained, 50k samples) |
| LLM Deception | MLX Qwen 1.5-2B (local, Apple Silicon) |
| Optimization (Novel) | TC-PSO + S-RRT (this repo) |
| Database | PostgreSQL + Alembic |
| Blockchain Log | Custom SHA-256 chain |
| Frontend | React + TailwindCSS |

---

## 👥 Authors

**Chameleon Research Team** — Semester 4 Cybersecurity ML Project, 2026
