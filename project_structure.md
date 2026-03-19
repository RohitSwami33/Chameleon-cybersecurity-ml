# Chameleon Project Directory Structure
```text
Chameleon/
├── .github
│   └── workflows
│       └── deploy.yml
├── Backend
│   ├── api
│   │   └── export
│   │       └── stix.py
│   ├── contracts
│   │   └── ChameleonLedger.sol
│   ├── data
│   │   ├── augmented_dataset.csv
│   │   ├── balance_dataset.py
│   │   ├── mongod.log.2025-11-22T14-12-55
│   │   ├── train_balanced.jsonl
│   │   ├── train.jsonl
│   │   ├── valid_balanced.jsonl
│   │   └── valid.jsonl
│   ├── docs
│   │   ├── confusion_matrix_50k.png
│   │   ├── INTEGRATION_GUIDE.md
│   │   ├── META_HEURISTICS_SUMMARY.md
│   │   ├── RRT_DOCUMENTATION.md
│   │   ├── s_rrt_memory_optimization.png
│   │   ├── tc_pso_vs_standard.png
│   │   ├── TEST_SUITE_DOCUMENTATION.md
│   │   ├── training_metrics_50k.png
│   │   └── walkthrough.md
│   ├── finetune_data
│   │   ├── augmented_dataset.csv
│   │   ├── balance_dataset.py
│   │   ├── train_balanced.jsonl
│   │   ├── train.jsonl
│   │   ├── valid_balanced.jsonl
│   │   └── valid.jsonl
│   ├── migrations
│   │   ├── versions
│   │   │   └── 20260216_initial_schema.py
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── models
│   │   ├── chameleon_char_cnn_gru.keras
│   │   ├── chameleon_lstm_m4_50k.pth
│   │   ├── chameleon_lstm_model.pt
│   │   ├── tokenizer_50k.json
│   │   └── tokenizer.pkl
│   ├── network
│   │   ├── server_rsa.key
│   │   └── ssh_honeypot.py
│   ├── scripts
│   │   ├── init_db.py
│   │   ├── seed_attacks.py
│   │   ├── train_50k_lstm.py
│   │   ├── train_bi_lstm_50k.py
│   │   ├── train_lstm_full.py
│   │   ├── train_lstm_quick.py
│   │   └── train_lstm.py
│   ├── sensors
│   │   └── sensor.py
│   ├── src
│   │   ├── api
│   │   │   ├── export
│   │   │   │   └── stix.py
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── main.py
│   │   │   └── pipeline.py
│   │   ├── core
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── database_postgres.py
│   │   │   ├── database.py
│   │   │   ├── models_sqlalchemy.py
│   │   │   └── models.py
│   │   ├── ml_engine
│   │   │   ├── __init__.py
│   │   │   ├── bilstm_inference.py
│   │   │   ├── inference.py
│   │   │   ├── local_inference.py
│   │   │   ├── ml_classifier.py
│   │   │   ├── ml_inference.py
│   │   │   └── simple_tokenizer.py
│   │   ├── optimization
│   │   │   ├── __init__.py
│   │   │   ├── benchmark_custom_optimizations.py
│   │   │   ├── generate_research_graphs.py
│   │   │   └── meta_heuristics.py
│   │   ├── utils
│   │   │   ├── __init__.py
│   │   │   ├── alert_manager.py
│   │   │   ├── attacker_session.py
│   │   │   ├── blockchain_logger.py
│   │   │   ├── blockchain_sync.py
│   │   │   ├── chatbot_service.py
│   │   │   ├── deception_engine_v2.py
│   │   │   ├── deception_engine.py
│   │   │   ├── integrity.py
│   │   │   ├── llm_controller.py
│   │   │   ├── login_rate_limiter.py
│   │   │   ├── mock_database.py
│   │   │   ├── report_generator.py
│   │   │   ├── tarpit_manager.py
│   │   │   ├── threat_intel_service.py
│   │   │   ├── threat_score.py
│   │   │   └── utils.py
│   │   └── __init__.py
│   ├── test_results
│   │   ├── COMPARISON_REPORT.md
│   │   ├── comparison_results.txt
│   │   ├── FINAL_PIPELINE_RESULTS.md
│   │   ├── full_suite_results.txt
│   │   ├── MODEL_PERFORMANCE_REPORT.md
│   │   ├── PIPELINE_TEST_RESULTS.md
│   │   ├── README.md
│   │   ├── s_rrt_results.txt
│   │   ├── tc_pso_and_proofs_results.txt
│   │   └── tc_pso_results.txt
│   ├── tests
│   │   ├── novel_equations
│   │   │   └── test_novel_equations_comprehensive.py
│   │   ├── results
│   │   │   ├── novel_equations_test_output.txt
│   │   │   ├── NOVEL_EQUATIONS_TEST_RESULTS.md
│   │   │   └── PROJECT_COMPARISON_REPORT.md
│   │   ├── __init__.py
│   │   ├── test_comparison_algorithms.py
│   │   ├── test_mathematical_proofs.py
│   │   ├── test_s_rrt_equations.py
│   │   └── test_tc_pso_equations.py
│   ├── .env.example
│   ├── alembic.ini
│   ├── chameleon_char_cnn_gru.keras
│   ├── chameleon_lstm_m4_50k.pth
│   ├── chameleon_lstm_model.pt
│   ├── conftest.py
│   ├── confusion_matrix_50k.png
│   ├── CONNECTION_AUDIT_REPORT.md
│   ├── dataset_integrity.json
│   ├── init_db.py
│   ├── INTEGRATION_GUIDE.md
│   ├── META_HEURISTICS_DOCUMENTATION.md
│   ├── META_HEURISTICS_SUMMARY.md
│   ├── NOVEL_EQUATIONS_IMPLEMENTATION_AUDIT.md
│   ├── pytest.ini
│   ├── refactor_imports.py
│   ├── requirements_ml.txt
│   ├── requirements.txt
│   ├── RRT_DOCUMENTATION.md
│   ├── s_rrt_memory_optimization.png
│   ├── seed_attacks.py
│   ├── tc_pso_vs_standard.png
│   ├── test_50k_model.py
│   ├── test_blockchain_sync.py
│   ├── test_chamaeleon.py
│   ├── test_honeytoken.py
│   ├── test_logs_validation.py
│   ├── test_logs.py
│   ├── test_meta_heuristics_rigorous.py
│   ├── test_payload.py
│   ├── test_pipeline_classification.py
│   ├── test_regex.py
│   ├── test_rigorous_pipeline.py
│   ├── TEST_SUITE_DOCUMENTATION.md
│   ├── test_system.py
│   ├── test_trap_execute.py
│   ├── tokenizer_50k.json
│   ├── tokenizer.pkl
│   ├── train_50k_lstm.py
│   ├── train_bi_lstm_50k.py
│   ├── train_lstm_full.py
│   ├── train_lstm_quick.py
│   ├── train_lstm.py
│   ├── training_history_50k.json
│   ├── training_history.json
│   ├── training_metrics_50k.png
│   └── verify_connections.py
├── data
│   └── __init__.py
├── docs
│   ├── architecture_timeline
│   │   ├── 01_deepseek_to_local_mlx_migration.md
│   │   ├── 02_handling_gpu_concurrency_and_locks.md
│   │   ├── 03_bilstm_and_deception_layer.md
│   │   ├── 04_rigorous_testing_and_validation.md
│   │   └── README.md
│   └── project_planning
│       ├── implementation_plan.md
│       ├── task.md
│       └── walkthrough.md
├── frontend
│   ├── public
│   │   └── vite.svg
│   ├── src
│   │   ├── assets
│   │   │   └── react.svg
│   │   ├── components
│   │   │   ├── dashboard
│   │   │   │   ├── LiveThreatFeed.jsx
│   │   │   │   ├── SRTDeceptionMap.jsx
│   │   │   │   ├── SystemEdgeNodeStatus.jsx
│   │   │   │   └── TCPSOTarpitMonitor.jsx
│   │   │   ├── ui
│   │   │   │   ├── CommandBar.css
│   │   │   │   ├── CommandBar.jsx
│   │   │   │   ├── FilterBadges.jsx
│   │   │   │   └── HelpModal.jsx
│   │   │   ├── AIChatbot.jsx
│   │   │   ├── AIOrb3D.jsx
│   │   │   ├── AttackChart.jsx
│   │   │   ├── AttackGlobeSimple.jsx
│   │   │   ├── AttackLogs.jsx
│   │   │   ├── AttackTerrainMap.jsx
│   │   │   ├── BlockchainExplorer.jsx
│   │   │   ├── BlockchainViz3D.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── DepthLayers.jsx
│   │   │   ├── GeoMap.jsx
│   │   │   ├── GlobalBackground.jsx
│   │   │   ├── GlobalGridBackground.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── LoginBackground3D.jsx
│   │   │   ├── LoginShield3D.jsx
│   │   │   ├── MerkleTree3D.jsx
│   │   │   ├── Navbar.jsx
│   │   │   ├── PageTransition.jsx
│   │   │   ├── ProtectedRoute.jsx
│   │   │   ├── ServerRack3D.jsx
│   │   │   ├── StatsCards.jsx
│   │   │   ├── TelemetryTable.jsx
│   │   │   ├── ThreatIntelFeed.jsx
│   │   │   ├── ThreatRadar3D.jsx
│   │   │   ├── ThreatScorePanel.jsx
│   │   │   ├── TiltCard.jsx
│   │   │   ├── TrapInterface.jsx
│   │   │   └── WorldMap.jsx
│   │   ├── config
│   │   │   └── api.js
│   │   ├── hooks
│   │   │   ├── useDashboard.js
│   │   │   ├── useMagneticTilt.js
│   │   │   └── useTerminal.js
│   │   ├── lib
│   │   │   ├── commandActions.js
│   │   │   ├── commandParser.js
│   │   │   └── exportUtils.js
│   │   ├── pages
│   │   │   ├── AdvancedSystemsPage.jsx
│   │   │   ├── AnalyticsPage.jsx
│   │   │   ├── AttackGlobePage.jsx
│   │   │   ├── ChatbotPage.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── DashboardOverview.jsx
│   │   │   └── ThreatIntelPage.jsx
│   │   ├── services
│   │   │   ├── api.js
│   │   │   └── dashboardApi.js
│   │   ├── stores
│   │   │   ├── useAttackStore.js
│   │   │   └── useAuthStore.js
│   │   ├── utils
│   │   │   └── helpers.js
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── config.js
│   │   ├── index.css
│   │   ├── index.css.bak
│   │   ├── main.jsx
│   │   └── trap.css
│   ├── .env
│   ├── .env.example
│   ├── .gitignore
│   ├── apply_red_theme.js
│   ├── DASHBOARD_IMPLEMENTATION_GUIDE.md
│   ├── eslint.config.js
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.js
│   ├── README.md
│   ├── requirements.txt
│   ├── revert_theme.js
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── walkthrough.md
├── models
│   └── __init__.py
├── scripts
│   └── __init__.py
├── src
│   ├── api
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── main.py
│   │   └── pipeline.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database_postgres.py
│   │   ├── database.py
│   │   ├── models_sqlalchemy.py
│   │   └── models.py
│   ├── ml_engine
│   │   ├── __init__.py
│   │   ├── bilstm_inference.py
│   │   ├── inference.py
│   │   ├── local_inference.py
│   │   ├── ml_classifier.py
│   │   ├── ml_inference.py
│   │   └── simple_tokenizer.py
│   ├── optimization
│   │   ├── __init__.py
│   │   ├── benchmark_custom_optimizations.py
│   │   ├── generate_research_graphs.py
│   │   └── meta_heuristics.py
│   ├── utils
│   │   ├── __init__.py
│   │   ├── alert_manager.py
│   │   ├── attacker_session.py
│   │   ├── blockchain_logger.py
│   │   ├── blockchain_sync.py
│   │   ├── chatbot_service.py
│   │   ├── deception_engine_v2.py
│   │   ├── deception_engine.py
│   │   ├── integrity.py
│   │   ├── llm_controller.py
│   │   ├── login_rate_limiter.py
│   │   ├── mock_database.py
│   │   ├── report_generator.py
│   │   ├── tarpit_manager.py
│   │   ├── threat_intel_service.py
│   │   ├── threat_score.py
│   │   └── utils.py
│   └── __init__.py
├── tests
│   ├── novel_equations
│   │   ├── __init__.py
│   │   └── test_novel_equations_comprehensive.py
│   ├── results
│   │   ├── __init__.py
│   │   ├── NOVEL_EQUATIONS_TEST_RESULTS.md
│   │   └── PROJECT_COMPARISON_REPORT.md
│   ├── __init__.py
│   ├── test_comparison_algorithms.py
│   ├── test_mathematical_proofs.py
│   ├── test_s_rrt_equations.py
│   └── test_tc_pso_equations.py
├── .gitattributes
├── .gitignore
├── CHAMELEON_DOCUMENTATION.md
├── custom_attack_data_6k.csv
├── custom_attack_data.csv
├── extract_tree.js
├── final_dataset.csv
├── ga_evolution_graph.png
├── generate_6k_dataset.py
├── generate_6k_deepseek_api.py
├── generate_attack_dataset.py
├── LOCAL_LLM_ARCHITECTURE.md
├── LSTM_MODEL_DOCUMENTATION.md
├── NOVEL_EQUATIONS_DOCUMENTATION.md
├── package-lock.json
├── package.json
├── pso_convergence_graph.png
├── README.md
├── RESEARCH_GRAPHS_DOCUMENTATION.md
├── ROLLBACK_SUMMARY.md
└── SECURITY.md

```
