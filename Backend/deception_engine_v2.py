"""
Advanced Progressive Deception Engine V2
Generates context-aware, stage-based deceptive responses that create a "Narrative of Failure"
"""
import random
import re
import uuid
from typing import Optional
from models import AttackType
from attacker_session import AttackerSession, advance_session_stage

class ProgressiveDeceptionEngine:
    """
    Advanced deception engine that creates progressive, believable error messages
    that make attackers think they're making progress while being monitored.
    """
    
    def __init__(self):
        # Common table names attackers look for
        self.common_tables = [
            "users", "admin", "accounts", "members", "customers",
            "login", "user_data", "profiles", "sessions", "auth"
        ]
        
        # Common column names attackers target
        self.common_columns = [
            "password", "passwd", "pwd", "pass", "username", "user",
            "email", "id", "admin", "role", "token", "hash", "salt"
        ]
        
        # Database-specific error codes
        self.db_error_codes = {
            "MySQL": {
                "syntax": 1064,
                "table_not_found": 1146,
                "column_not_found": 1054,
                "access_denied": 1045,
                "permission_denied": 1142
            },
            "PostgreSQL": {
                "syntax": "42601",
                "table_not_found": "42P01",
                "column_not_found": "42703",
                "access_denied": "28P01",
                "permission_denied": "42501"
            },
            "SQLite": {
                "syntax": 1,
                "table_not_found": 1,
                "column_not_found": 1,
                "access_denied": 23,
                "permission_denied": 23
            }
        }
        
        # Flavor text to add realism
        self.flavor_texts = [
            "Please contact your database administrator if the problem persists.",
            "Check the manual for more information.",
            "This error has been logged for security review.",
            "For assistance, contact support@example.com",
            "Error logged to /var/log/mysql/error.log",
            "Connection ID: {conn_id}",
            "Thread ID: {thread_id}"
        ]
    
    def extract_snippet(self, raw_input: str, max_length: int = 50) -> str:
        """
        Extract a meaningful snippet from the attack input for error messages.
        
        Args:
            raw_input: The attacker's input
            max_length: Maximum length of snippet
            
        Returns:
            Sanitized snippet for error message
        """
        # Remove excessive whitespace
        snippet = ' '.join(raw_input.split())
        
        # Truncate if too long
        if len(snippet) > max_length:
            snippet = snippet[:max_length] + "..."
        
        # Escape quotes for SQL error messages
        snippet = snippet.replace("'", "\\'")
        
        return snippet
    
    def extract_table_name(self, raw_input: str) -> Optional[str]:
        """
        Try to extract a table name from the SQL injection attempt.
        
        Args:
            raw_input: The attacker's input
            
        Returns:
            Extracted table name or None
        """
        input_lower = raw_input.lower()
        
        # Look for common table names in the input
        for table in self.common_tables:
            if table in input_lower:
                return table
        
        # Try to extract from FROM clause
        from_match = re.search(r'from\s+([a-zA-Z_][a-zA-Z0-9_]*)', input_lower)
        if from_match:
            return from_match.group(1)
        
        # Default fallback
        return random.choice(self.common_tables)
    
    def extract_column_name(self, raw_input: str) -> Optional[str]:
        """
        Try to extract a column name from the SQL injection attempt.
        
        Args:
            raw_input: The attacker's input
            
        Returns:
            Extracted column name or None
        """
        input_lower = raw_input.lower()
        
        # Look for common column names
        for column in self.common_columns:
            if column in input_lower:
                return column
        
        # Try to extract from SELECT clause
        select_match = re.search(r'select\s+([a-zA-Z_][a-zA-Z0-9_]*)', input_lower)
        if select_match:
            return select_match.group(1)
        
        # Default fallback
        return random.choice(self.common_columns)
    
    def generate_fake_incident_id(self) -> str:
        """Generate a realistic-looking incident ID."""
        return f"INC-{uuid.uuid4().hex[:8].upper()}"
    
    def generate_fake_connection_id(self) -> int:
        """Generate a fake database connection ID."""
        return random.randint(1000, 99999)
    
    def add_flavor_text(self, message: str, session: AttackerSession) -> str:
        """
        Add realistic flavor text to error messages.
        
        Args:
            message: Base error message
            session: Attacker session for context
            
        Returns:
            Enhanced message with flavor text
        """
        if random.random() < 0.3:  # 30% chance to add flavor
            flavor = random.choice(self.flavor_texts)
            flavor = flavor.format(
                conn_id=self.generate_fake_connection_id(),
                thread_id=random.randint(1, 999)
            )
            return f"{message}\n{flavor}"
        return message
    
    async def generate_sqli_response(
        self, 
        raw_input: str, 
        session: AttackerSession
    ) -> str:
        """
        Generate progressive SQL injection deception response.
        
        Stage 1: Syntax error (makes attacker fix their SQL)
        Stage 2: Table not found (makes attacker enumerate tables)
        Stage 3: Column not found (makes attacker enumerate columns)
        Stage 4: Permission denied (ultimate frustration)
        
        Args:
            raw_input: The attack payload
            session: Current attacker session
            
        Returns:
            Deceptive error message appropriate for the stage
        """
        db_type = session.db_type
        stage = session.current_stage
        
        # Stage 1: Syntax Error
        if stage == 1:
            snippet = self.extract_snippet(raw_input, 40)
            error_code = self.db_error_codes.get(db_type, {}).get("syntax", 1064)
            
            if db_type == "MySQL":
                message = f"Error {error_code}: You have an error in your SQL syntax; check the manual that corresponds to your {db_type} server version for the right syntax to use near '{snippet}' at line 1"
            elif db_type == "PostgreSQL":
                message = f"ERROR: syntax error at or near \"{snippet}\"\nLINE 1: {snippet}\n        ^\nSQL state: {error_code}"
            else:  # SQLite
                message = f"Error: near \"{snippet}\": syntax error"
            
            # Advance to next stage for next attempt
            await advance_session_stage(session)
            
            return self.add_flavor_text(message, session)
        
        # Stage 2: Table Not Found
        elif stage == 2:
            # Extract or guess table name
            table_name = self.extract_table_name(raw_input)
            session.guessed_table = table_name
            
            error_code = self.db_error_codes.get(db_type, {}).get("table_not_found", 1146)
            
            if db_type == "MySQL":
                message = f"Error {error_code}: Table 'webapp_db.{table_name}' doesn't exist"
            elif db_type == "PostgreSQL":
                message = f"ERROR: relation \"{table_name}\" does not exist\nLINE 1: SELECT * FROM {table_name}\n                      ^\nSQL state: {error_code}"
            else:  # SQLite
                message = f"Error: no such table: {table_name}"
            
            # Advance to next stage
            await advance_session_stage(session)
            
            return self.add_flavor_text(message, session)
        
        # Stage 3: Column Not Found
        elif stage == 3:
            # Extract or guess column name
            column_name = self.extract_column_name(raw_input)
            session.guessed_column = column_name
            
            table_name = session.guessed_table or "users"
            error_code = self.db_error_codes.get(db_type, {}).get("column_not_found", 1054)
            
            if db_type == "MySQL":
                message = f"Error {error_code}: Unknown column '{column_name}' in 'field list'"
            elif db_type == "PostgreSQL":
                message = f"ERROR: column \"{column_name}\" does not exist\nLINE 1: SELECT {column_name} FROM {table_name}\n               ^\nSQL state: {error_code}"
            else:  # SQLite
                message = f"Error: no such column: {column_name}"
            
            # Advance to final stage
            await advance_session_stage(session)
            
            return self.add_flavor_text(message, session)
        
        # Stage 4: Permission Denied (Final Stage)
        else:
            error_code = self.db_error_codes.get(db_type, {}).get("access_denied", 1045)
            
            # Get the IP from session (we'll need to pass this)
            # For now, use a generic message
            if db_type == "MySQL":
                message = f"Error {error_code}: Access denied for user 'webapp_user'@'localhost' (using password: YES)"
            elif db_type == "PostgreSQL":
                message = f"FATAL: permission denied for table {session.guessed_table or 'users'}\nSQL state: {error_code}"
            else:  # SQLite
                message = f"Error: attempt to write a readonly database"
            
            # Stay at stage 4 - they're stuck now
            return self.add_flavor_text(message, session)
    
    async def generate_xss_response(
        self, 
        raw_input: str, 
        session: AttackerSession
    ) -> str:
        """
        Generate progressive XSS deception response.
        
        Stage 1: CSP violation (makes attacker try to bypass)
        Stage 2: Input sanitization (makes attacker try encoding)
        Stage 3: Obfuscation detection (ultimate frustration)
        
        Args:
            raw_input: The attack payload
            session: Current attacker session
            
        Returns:
            Deceptive error message appropriate for the stage
        """
        stage = session.current_stage
        
        # Stage 1: CSP Violation
        if stage == 1:
            message = "Refused to execute inline script because it violates the following Content Security Policy directive: \"script-src 'self' https://cdn.trusted.com https://analytics.trusted.com\". Either the 'unsafe-inline' keyword, a hash ('sha256-...'), or a nonce ('nonce-...') is required to enable inline execution."
            
            await advance_session_stage(session)
            return message
        
        # Stage 2: Input Sanitization
        elif stage == 2:
            # Extract dangerous characters
            dangerous_chars = set()
            for char in ['<', '>', '/', '"', "'", '(', ')']:
                if char in raw_input:
                    dangerous_chars.add(char)
            
            chars_list = ' '.join(dangerous_chars) if dangerous_chars else '< > / " \''
            
            message = f"Input Blocked: Potential XSS detected. The following characters were stripped: {chars_list}\nYour input has been sanitized for security. Incident ID: {self.generate_fake_incident_id()}"
            
            await advance_session_stage(session)
            return message
        
        # Stage 3: Obfuscation Detection (Final Stage)
        else:
            incident_id = self.generate_fake_incident_id()
            message = f"Security Alert: Obfuscated or encoded script content detected. Your request has been logged and blocked.\nIncident ID: {incident_id}\nTimestamp: {session.last_seen.isoformat()}\nThis incident has been reported to the security team."
            
            # Stay at stage 3
            return message
    
    async def generate_progressive_response(
        self, 
        attack_type: AttackType, 
        raw_input: str,
        session: AttackerSession
    ) -> str:
        """
        Main entry point for generating progressive deception responses.
        
        Args:
            attack_type: Type of attack detected
            raw_input: The attack payload
            session: Current attacker session
            
        Returns:
            Context-aware deceptive response
        """
        # Update session attack type if not set
        if not session.attack_type:
            session.attack_type = attack_type.value
        
        # Generate response based on attack type
        if attack_type == AttackType.SQLI:
            return await self.generate_sqli_response(raw_input, session)
        
        elif attack_type == AttackType.XSS:
            return await self.generate_xss_response(raw_input, session)
        
        # For other attack types, use generic responses
        elif attack_type == AttackType.SSI:
            return "Error: Server-side includes are disabled on this server. SSI directives have been stripped from your input."
        
        elif attack_type == AttackType.BRUTE_FORCE:
            attempts_left = max(0, 3 - session.attempt_count)
            if attempts_left > 0:
                return f"Invalid credentials. {attempts_left} attempts remaining before account lockout."
            else:
                return "Account temporarily locked due to multiple failed login attempts. Please try again in 15 minutes."
        
        else:  # BENIGN
            return "Request processed successfully."

# Global instance
progressive_deception_engine = ProgressiveDeceptionEngine()
