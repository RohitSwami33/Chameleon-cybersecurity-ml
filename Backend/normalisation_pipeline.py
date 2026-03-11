"""
NormalisationPipeline — Multi-Layer Input Normalisation
========================================================

Seven-pass normalisation pipeline that canonicalises attack payloads
before they reach the BiLSTM/MLX classifier, defeating encoding tricks.

Pass 1: Iterative URL decode until stable
Pass 2: HTML entity decode
Pass 3: Unicode normalisation (NFKC)
Pass 4: Null byte stripping
Pass 5: SQL comment removal
Pass 6: Keyword reconstruction (S/**/ELECT → SELECT)
Pass 7: Whitespace normalisation

The original payload is always preserved separately for logging.
"""

import html
import logging
import re
import unicodedata
from urllib.parse import unquote

logger = logging.getLogger(__name__)


class NormalisationPipeline:
    """
    Multi-layer payload normalisation to produce canonical form.
    
    Usage:
        pipeline = NormalisationPipeline()
        canonical = pipeline.normalise(raw_payload)
    """

    # SQL keywords that attackers try to break with inline comments
    _SQL_KEYWORDS = [
        "SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "UNION",
        "FROM", "WHERE", "TABLE", "ALTER", "CREATE", "EXEC",
        "EXECUTE", "HAVING", "ORDER", "GROUP", "INTO", "VALUES",
        "INFORMATION_SCHEMA", "CONCAT", "SUBSTRING", "CHAR",
        "DECLARE", "WAITFOR", "BENCHMARK", "SLEEP",
    ]

    # Regex for SQL inline/line comments
    _SQL_INLINE_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
    _SQL_LINE_COMMENT_DOUBLE_DASH = re.compile(r"--[^\r\n]*")
    _SQL_LINE_COMMENT_HASH = re.compile(r"#[^\r\n]*")

    def normalise(self, payload: str) -> str:
        """
        Run all normalisation passes and return canonical payload.

        Args:
            payload: Raw input string from attacker.

        Returns:
            Canonicalised payload string.
        """
        if not payload:
            return payload

        try:
            result = payload

            # Pass 1: Iterative URL decode
            result = self._pass_url_decode(result)

            # Pass 2: HTML entity decode
            result = self._pass_html_decode(result)

            # Pass 3: Unicode normalisation (NFKC)
            result = self._pass_unicode_normalise(result)

            # Pass 4: Null byte stripping
            result = self._pass_null_strip(result)

            # Pass 5: SQL comment removal
            result = self._pass_sql_comment_removal(result)

            # Pass 6: Keyword reconstruction
            result = self._pass_keyword_reconstruction(result)

            # Pass 7: Whitespace normalisation
            result = self._pass_whitespace_normalise(result)

            if result != payload:
                logger.debug(
                    "NormalisationPipeline: payload changed | "
                    f"original_len={len(payload)} -> normalised_len={len(result)}"
                )

            return result

        except Exception as e:
            logger.warning(f"NormalisationPipeline: error during normalisation: {e}")
            # Fallback: return original payload on error
            return payload

    # ── Individual passes ─────────────────────────────────────────────

    @staticmethod
    def _pass_url_decode(s: str) -> str:
        """Iterative URL decode until stable (handles double/triple encoding)."""
        prev = None
        current = s
        max_iterations = 5
        i = 0
        while current != prev and i < max_iterations:
            prev = current
            current = unquote(current)
            i += 1
        return current

    @staticmethod
    def _pass_html_decode(s: str) -> str:
        """HTML entity decode."""
        return html.unescape(s)

    @staticmethod
    def _pass_unicode_normalise(s: str) -> str:
        """
        Unicode normalisation (NFKC).
        Collapses fullwidth characters (e.g., ＳＥＬＥＣＴ → SELECT).
        """
        return unicodedata.normalize("NFKC", s)

    @staticmethod
    def _pass_null_strip(s: str) -> str:
        """Strip null bytes."""
        return s.replace("\x00", "")

    @classmethod
    def _pass_sql_comment_removal(cls, s: str) -> str:
        """Remove SQL inline comments (/**/), double-dash (--), and hash (#) comments."""
        result = cls._SQL_INLINE_COMMENT.sub("", s)
        result = cls._SQL_LINE_COMMENT_DOUBLE_DASH.sub("", result)
        result = cls._SQL_LINE_COMMENT_HASH.sub("", result)
        return result

    @classmethod
    def _pass_keyword_reconstruction(cls, s: str) -> str:
        """
        Reconstruct SQL keywords broken by inline comments.

        Detects patterns like S/**/ELECT, UN/**/ION and collapses them
        back to SELECT, UNION.
        """
        result = s
        for keyword in cls._SQL_KEYWORDS:
            # Build a regex that matches the keyword letters separated by
            # optional inline comments and/or whitespace
            pattern_parts = []
            for char in keyword:
                pattern_parts.append(re.escape(char))
            # Match each character of the keyword separated by optional /**/ or whitespace
            regex_str = r"(?:/\*.*?\*/|\s)*".join(pattern_parts)
            regex = re.compile(regex_str, re.IGNORECASE | re.DOTALL)

            def _replacer(m):
                # Extract only alpha chars to reconstruct keyword
                alpha_only = re.sub(r"[^a-zA-Z_]", "", m.group())
                if alpha_only.upper() == keyword:
                    return keyword
                return m.group()

            result = regex.sub(_replacer, result)
        return result

    @staticmethod
    def _pass_whitespace_normalise(s: str) -> str:
        """Collapse multiple whitespace characters into single space, strip edges."""
        return " ".join(s.split())


# Global singleton
normalisation_pipeline = NormalisationPipeline()
