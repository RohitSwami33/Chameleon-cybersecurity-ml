"""
normaliser.py — Chameleon ML Pre-processing Pipeline
Novel Algorithms: NFKC-HCM, SMN, WCP, TLN

Apply normalise_pipeline() BEFORE every classification call.
The raw command must be logged BEFORE normalisation.
"""
import re
import unicodedata


# ============================================================
# EC-025: NFKC-HCM — Homoglyph Collapse Map
# ============================================================

HOMOGLYPH_MAP: dict = {
    # Cyrillic to Latin
    '\u0430': 'a', '\u0435': 'e', '\u0440': 'r', '\u0441': 'c',
    '\u043e': 'o', '\u0445': 'x', '\u0443': 'y', '\u0442': 't',
    '\u0412': 'B', '\u041a': 'K', '\u041c': 'M', '\u041d': 'H',
    '\u041e': 'O', '\u0420': 'P', '\u0421': 'C', '\u0422': 'T',
    '\u0425': 'X', '\u0410': 'A', '\u0415': 'E',
    # Greek to Latin
    '\u03b1': 'a', '\u03b2': 'B', '\u03b5': 'e', '\u03b9': 'i',
    '\u03ba': 'k', '\u03bd': 'v', '\u03bf': 'o', '\u03c1': 'p',
    '\u03c5': 'u', '\u03c7': 'x', '\u0391': 'A', '\u0392': 'B',
    '\u0395': 'E', '\u0397': 'H', '\u0399': 'I', '\u039a': 'K',
    '\u039c': 'M', '\u039d': 'N', '\u039f': 'O', '\u03a1': 'P',
    '\u03a4': 'T', '\u03a5': 'Y', '\u03a7': 'X',
    # Full-width ASCII to half-width
    **{chr(0xFF01 + i): chr(0x21 + i) for i in range(94)},
}


def normalise_command(command: str) -> str:
    """
    EC-025: NFKC normalisation + Homoglyph Collapse.
    Novel algorithm: NFKC-HCM (Normalization Form KC - Homoglyph Collapse Map)
    Collapses Unicode lookalikes to prevent ML evasion.
    """
    nfkc = unicodedata.normalize('NFKC', command)
    return ''.join(HOMOGLYPH_MAP.get(ch, ch) for ch in nfkc)


# ============================================================
# EC-026: SMN — Shell Metacharacter Normalisation
# ============================================================

_SMN_PATTERNS = [
    # Variable expansions to remove
    (re.compile(r'\$[@*]|\$[0-9]'), ''),
    # Process substitution
    (re.compile(r'<\([^)]*\)|>\([^)]*\)'), '[proc_sub]'),
    # Arithmetic expansion
    (re.compile(r'\$\(\([^)]*\)\)'), '[arith]'),
    # Command substitution
    (re.compile(r'\$\([^)]*\)'), '[subshell]'),
    # Parameter expansion with default
    (re.compile(r'\$\{[^}]*:-([^}]*)\}'), r'\1'),
    # Parameter expansion
    (re.compile(r'\$\{[^}]+\}'), ''),
    # Simple variable
    (re.compile(r'\$[a-zA-Z_][a-zA-Z0-9_]*'), ''),
    # Multiple spaces to single
    (re.compile(r'  +'), ' '),
]


def smn_normalise(command: str) -> str:
    """
    EC-026: SMN (Shell Metacharacter Normalisation).
    Novel algorithm: Collapses shell metachar expansions to canonical form.
    Prevents evasion via $(), ${}, $variable, etc.
    """
    result = command
    for pattern, replacement in _SMN_PATTERNS:
        result = pattern.sub(replacement, result)
    return result.strip()


# ============================================================
# EC-028: WCP — Whitespace Collapsed Path
# ============================================================


def wcp_normalise(command: str) -> str:
    """
    EC-028: WCP (Whitespace Collapsed Path).
    Collapses spaced path separators to prevent evasion.
    '. . / . . /' -> '../../'
    """
    result = re.sub(r'\.\s+\.', '..', command)
    result = re.sub(r'\s*/\s*', '/', result)
    result = re.sub(r'\s*\.\s*(?=[^.])', '.', result)
    return result


# ============================================================
# EC-031: TLN — Template Literal Normalisation
# ============================================================


def tln_normalise(command: str) -> str:
    """
    EC-031: TLN (Template Literal Normalisation).
    Novel algorithm: Converts JS template literals to function calls.
    alert`1` -> alert(1)
    Prevents XSS evasion via template literal syntax.
    """
    return re.sub(r'(\b[a-zA-Z_$][a-zA-Z0-9_$.]*)`([^`]*)`', r'\1(\2)', command)


# ============================================================
# Full Pipeline
# ============================================================

def normalise_pipeline(raw_command: str) -> str:
    """
    Full normalisation pipeline — apply BEFORE every classification call.
    
    Novel combined algorithm: NFKC-HCM + SMN + WCP + TLN
    
    Step 1: NFKC-HCM (Unicode homoglyphs)
    Step 2: SMN (shell metachar expansion)
    Step 3: WCP (spaced path traversal)
    Step 4: TLN (JS template literal evasion)
    
    IMPORTANT: Log the raw command BEFORE calling this function.
    The normalised version is only for classification, not logging.
    """
    s1 = normalise_command(raw_command)
    s2 = smn_normalise(s1)
    s3 = wcp_normalise(s2)
    s4 = tln_normalise(s3)
    return s4
