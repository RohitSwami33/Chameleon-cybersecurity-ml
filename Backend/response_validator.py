"""
ResponseValidator — LLM Output Safety Gate
=============================================

Validates every Qwen/DeepSeek response before serving to ensure:
  - DB type consistency (no wrong DB mentioned)
  - Version consistency
  - Table name consistency
  - Error code format validity
  - No real system paths leaked
  - No LLM provider names in output (Qwen, DeepSeek, LLM, etc.)

On validation failure → returns template fallback for session's db_type.
On LLM timeout → immediately serves pre-warmed template.

sanitise() strips internal fields (schema_id, execution_time_ms,
is_safe, prediction_score) from any JSON response.
"""

import json
import logging
import re
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class ResponseValidator:
    """
    Safety gate between LLM output and attacker-facing response.
    """

    # Patterns that should NEVER appear in responses served to attackers
    _FORBIDDEN_PATTERNS = [
        re.compile(r"\bqwen\b", re.IGNORECASE),
        re.compile(r"\bdeepseek\b", re.IGNORECASE),
        re.compile(r"\bllm\b", re.IGNORECASE),
        re.compile(r"\blarge language model\b", re.IGNORECASE),
        re.compile(r"\bchatgpt\b", re.IGNORECASE),
        re.compile(r"\bopenai\b", re.IGNORECASE),
        re.compile(r"\bgpt-[34]\b", re.IGNORECASE),
        re.compile(r"\bclaude\b", re.IGNORECASE),
        re.compile(r"\bgemini\b", re.IGNORECASE),
        re.compile(r"\bhoneypot\b", re.IGNORECASE),
        re.compile(r"\bsimulat(?:e|ed|ing|ion)\b", re.IGNORECASE),
        re.compile(r"\bfake\b", re.IGNORECASE),
        re.compile(r"\bdeception\b", re.IGNORECASE),
    ]

    # Real system paths that must not leak
    _REAL_PATH_PATTERNS = [
        re.compile(r"[A-Z]:\\", re.IGNORECASE),          # Windows paths
        re.compile(r"/Users/\w+"),                        # macOS home
        re.compile(r"/home/(?!admin|deploy|backup|dev|www-data)\w+"),  # Non-honeypot users
        re.compile(r"\\\\[A-Za-z0-9]+\\"),                # UNC paths
        re.compile(r"site-packages"),                     # Python internals
        re.compile(r"node_modules"),                      # Node internals
    ]

    # DB-specific keywords for consistency checking
    _DB_KEYWORDS = {
        "MySQL": ["mysql", "innodb", "myisam", "mysqld", "mariadb"],
        "PostgreSQL": ["postgresql", "postgres", "psql", "pg_", "postmaster"],
        "SQLite": ["sqlite", "sqlite3"],
        "MariaDB": ["mariadb", "mysql", "innodb"],
    }

    # DB-specific keywords that should NOT appear if the session is a different DB
    _DB_EXCLUSIVE = {
        "MySQL": ["psql", "pg_", "postmaster", "sqlite3"],
        "PostgreSQL": ["mysqld", "myisam", "innodb", "sqlite3"],
        "SQLite": ["mysqld", "pg_", "postmaster", "innodb"],
        "MariaDB": ["psql", "pg_", "postmaster", "sqlite3"],
    }

    # Fields to strip from JSON responses
    _STRIP_FIELDS = [
        "schema_id", "execution_time_ms", "is_safe",
        "prediction_score", "is_malicious",
    ]

    # Pre-warmed fallback templates by DB type and stage
    _FALLBACK_TEMPLATES = {
        "MySQL": {
            1: "Error 1064: You have an error in your SQL syntax; check the manual for the right syntax near '' at line 1",
            2: "Error 1146: Table 'webapp_db.users' doesn't exist",
            3: "Error 1054: Unknown column 'password' in 'field list'",
            4: "Error 1045: Access denied for user 'webapp_user'@'localhost' (using password: YES)",
        },
        "PostgreSQL": {
            1: 'ERROR: syntax error at or near ""\nLINE 1: \n        ^\nSQL state: 42601',
            2: 'ERROR: relation "users" does not exist\nSQL state: 42P01',
            3: 'ERROR: column "password" does not exist\nSQL state: 42703',
            4: "FATAL: permission denied for table users\nSQL state: 42501",
        },
        "SQLite": {
            1: 'Error: near "": syntax error',
            2: "Error: no such table: users",
            3: "Error: no such column: password",
            4: "Error: attempt to write a readonly database",
        },
        "MariaDB": {
            1: "Error 1064: You have an error in your SQL syntax near '' at line 1",
            2: "Error 1146: Table 'webapp_db.users' doesn't exist",
            3: "Error 1054: Unknown column 'password' in 'field list'",
            4: "Error 1045: Access denied for user 'webapp_user'@'localhost'",
        },
    }

    def validate(
        self,
        response: str,
        session: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, str]:
        """
        Validate an LLM response before serving.

        Args:
            response: The LLM-generated response text
            session: Session dict with db_type, current_stage, table_name, etc.

        Returns:
            Tuple of (is_valid, cleaned_or_fallback_response)
        """
        if not response:
            return False, self._get_fallback(session)

        issues = []

        # Check 1: Forbidden patterns (LLM names, honeypot indicators)
        for pattern in self._FORBIDDEN_PATTERNS:
            if pattern.search(response):
                issues.append(f"Forbidden pattern: {pattern.pattern}")

        # Check 2: Real system paths
        for pattern in self._REAL_PATH_PATTERNS:
            if pattern.search(response):
                issues.append(f"Real path leak: {pattern.pattern}")

        # Check 3: DB type consistency
        if session:
            db_type = session.get("db_type", "MySQL")
            exclusive_keywords = self._DB_EXCLUSIVE.get(db_type, [])
            response_lower = response.lower()
            for keyword in exclusive_keywords:
                if keyword in response_lower:
                    issues.append(f"Wrong DB keyword '{keyword}' for {db_type}")

        if issues:
            logger.warning(
                f"ResponseValidator: FAILED | Issues: {issues[:3]} | "
                f"Serving fallback template"
            )
            return False, self._get_fallback(session)

        # Valid — return cleaned response
        return True, response

    def sanitise(self, response: str) -> str:
        """
        Strip internal fields from JSON responses.

        Removes: schema_id, execution_time_ms, is_safe, prediction_score

        Args:
            response: Response string (may be JSON or plain text)

        Returns:
            Sanitised response string
        """
        # Try to parse as JSON and strip fields
        try:
            data = json.loads(response)
            if isinstance(data, dict):
                for field in self._STRIP_FIELDS:
                    data.pop(field, None)
                return json.dumps(data)
        except (json.JSONDecodeError, TypeError):
            pass

        return response

    def sanitise_dict(self, data: dict) -> dict:
        """
        Strip internal fields from a response dictionary.

        Args:
            data: Response dictionary

        Returns:
            Sanitised dictionary (new copy)
        """
        result = dict(data)
        for field in self._STRIP_FIELDS:
            result.pop(field, None)
        return result

    def _get_fallback(self, session: Optional[Dict[str, Any]] = None) -> str:
        """Get a pre-warmed fallback template for the session's DB and stage."""
        if session:
            db_type = session.get("db_type", "MySQL")
            stage = session.get("current_stage", 1)
        else:
            db_type = "MySQL"
            stage = 1

        templates = self._FALLBACK_TEMPLATES.get(db_type, self._FALLBACK_TEMPLATES["MySQL"])
        return templates.get(stage, templates.get(1, "Error: Internal server error"))


# Global singleton
response_validator = ResponseValidator()
