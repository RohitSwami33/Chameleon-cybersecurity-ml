import os
import re

SHIMS = {
    # optimization
    'meta_heuristics': 'src.optimization.meta_heuristics',
    'benchmark_custom_optimizations': 'src.optimization.benchmark_custom_optimizations',
    'generate_research_graphs': 'src.optimization.generate_research_graphs',
    # ml_engine
    'local_inference': 'src.ml_engine.local_inference',
    'bilstm_inference': 'src.ml_engine.bilstm_inference',
    'ml_classifier': 'src.ml_engine.ml_classifier',
    'ml_inference': 'src.ml_engine.ml_inference',
    'inference': 'src.ml_engine.inference',
    'simple_tokenizer': 'src.ml_engine.simple_tokenizer',
    # core
    'config': 'src.core.config',
    'models': 'src.core.models',
    'models_sqlalchemy': 'src.core.models_sqlalchemy',
    'database': 'src.core.database',
    'database_postgres': 'src.core.database_postgres',
    # api
    'pipeline': 'src.api.pipeline',
    'auth': 'src.api.auth',
    # utils
    'attacker_session': 'src.utils.attacker_session',
    'tarpit_manager': 'src.utils.tarpit_manager',
    'alert_manager': 'src.utils.alert_manager',
    'login_rate_limiter': 'src.utils.login_rate_limiter',
    'report_generator': 'src.utils.report_generator',
    'utils': 'src.utils.utils',
    'integrity': 'src.utils.integrity',
    'threat_score': 'src.utils.threat_score',
    'threat_intel_service': 'src.utils.threat_intel_service',
    'chatbot_service': 'src.utils.chatbot_service',
    'llm_controller': 'src.utils.llm_controller',
    'blockchain_logger': 'src.utils.blockchain_logger',
    'blockchain_sync': 'src.utils.blockchain_sync',
    'deception_engine': 'src.utils.deception_engine',
    'deception_engine_v2': 'src.utils.deception_engine_v2',
    'mock_database': 'src.utils.mock_database',
}

search_dirs = ["src", "tests", "scripts", "network", "sensors", "migrations"]

changed_files = 0
for d in search_dirs:
    for root, _, files in os.walk(d):
        for f in files:
            if f.endswith(".py"):
                filepath = os.path.join(root, f)
                with open(filepath, 'r') as fp:
                    content = fp.read()
                
                original_content = content
                
                for mod, new_mod in SHIMS.items():
                    # replace `from module import` with `from src.category.module import`
                    content = re.sub(rf'^from\s+{mod}\s+import', f'from {new_mod} import', content, flags=re.MULTILINE)
                    # replace `import module` with `import src.category.module`
                    # or better: `import src.category.module as module` if they only use `module.`
                    # actually they usually do `from models import ...`.
                    # Let's see if there are plain imports.
                    content = re.sub(rf'^import\s+{mod}\b', f'import {new_mod} as {mod}', content, flags=re.MULTILINE)
                    
                if content != original_content:
                    with open(filepath, 'w') as fp:
                        fp.write(content)
                    print(f"Refactored {filepath}")
                    changed_files += 1

print(f"Refactored {changed_files} files.")

# Now delete the shim files at root to keep it completely clean!
deleted = 0
for mod in SHIMS.keys():
    shim_file = f"{mod}.py"
    if os.path.exists(shim_file):
        os.remove(shim_file)
        deleted += 1
print(f"Deleted {deleted} shim files from root.")
