import random
from models import AttackType, DeceptionResponse
from config import settings

class DeceptionEngine:
    """
    Adaptive Deception Engine - Generates fake error messages based on attack type
    to mislead attackers while logging real attacks internally.
    """
    def __init__(self):
        # SQLi fake error messages - mimic real database errors
        self.sql_errors = [
            "Error: You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '' at line 1",
            "MySQL Error 1064: Syntax error near 'SELECT' at line 1",
            "Table 'users' doesn't exist in database 'production_db'",
            "Access denied for user 'root'@'localhost' (using password: YES)",
            "Unclosed quotation mark after the character string",
            "Column 'username' in where clause is ambiguous",
            "Unknown column 'admin' in 'field list'",
            "Operand should contain 1 column(s)",
            "Subquery returns more than 1 row",
            "Error 1146: Table 'app.sessions' doesn't exist"
        ]
        
        # XSS fake error messages - mimic JavaScript/DOM errors
        self.xss_errors = [
            "Input validated successfully. Content sanitized.",
            "Form submitted. Thank you for your feedback.",
            "Profile updated successfully.",
            "Comment added to moderation queue.",
            "Error: Invalid HTML detected. Content has been escaped.",
            "Security filter applied. Special characters removed.",
            "Content-Security-Policy violation detected and blocked.",
            "DOM manipulation prevented by security policy.",
            "Script execution blocked by XSS protection.",
            "Unsafe inline script detected and neutralized."
        ]
        
        # SSI fake error messages
        self.ssi_errors = [
            "Server-side includes are disabled on this server.",
            "Error: SSI directives not allowed in user input.",
            "Request processed. Server configuration prevents SSI execution.",
            "Input sanitized successfully. SSI tags removed.",
            "Apache SSI module not enabled.",
            "SSI parsing disabled for security reasons.",
            "Include directives are not permitted in this context."
        ]
        
        # Brute force fake messages
        self.brute_force_errors = [
            "Invalid credentials. Please try again.",
            "Login failed. 2 attempts remaining.",
            "Account locked due to suspicious activity.",
            "Incorrect password. Please check your credentials.",
            "Authentication failed. Account will be locked after 3 failed attempts.",
            "Too many failed login attempts. Please try again in 15 minutes."
        ]
        
        # Benign responses
        self.benign_responses = [
            "Request processed successfully.",
            "Operation completed.",
            "Data retrieved successfully.",
            "OK",
            "Success: Your request has been processed.",
            "200 OK - Request completed."
        ]
        
        # Generic error for unknown attack types
        self.generic_errors = [
            "Bad Request: Invalid input detected.",
            "Error 400: Malformed request syntax.",
            "Request could not be processed. Please check your input.",
            "Invalid request format.",
            "Error: Request validation failed."
        ]
        
        # Map attack types to error lists
        self.responses = {
            AttackType.SQLI: self.sql_errors,
            AttackType.XSS: self.xss_errors,
            AttackType.SSI: self.ssi_errors,
            AttackType.BRUTE_FORCE: self.brute_force_errors,
            AttackType.BENIGN: self.benign_responses
        }

    def get_deceptive_error(self, attack_type: AttackType, input_snippet: str = "") -> str:
        """
        Generate a deceptive error message based on attack type and input.
        
        Args:
            attack_type: The predicted attack type
            input_snippet: Optional snippet of the attack input for context
            
        Returns:
            A fake error message appropriate for the attack type
        """
        message_list = self.responses.get(attack_type, self.generic_errors)
        message = random.choice(message_list)
        
        # Add some context-aware variations for SQLi
        if attack_type == AttackType.SQLI and input_snippet:
            if "union" in input_snippet.lower():
                message = "Error: UNION query with different number of columns"
            elif "drop" in input_snippet.lower():
                message = "Error: DROP command denied to user 'webapp'@'localhost'"
            elif "information_schema" in input_snippet.lower():
                message = "Error: SELECT command denied on table 'information_schema.tables'"
        
        return message

    def generate_response(self, attack_type: AttackType, apply_delay: float, input_snippet: str = "") -> DeceptionResponse:
        """
        Generate a complete deception response with appropriate HTTP status code.
        
        Args:
            attack_type: The predicted attack type
            apply_delay: Delay applied by tarpit
            input_snippet: Optional snippet of the attack input
            
        Returns:
            DeceptionResponse with fake message and appropriate status code
        """
        # Get deceptive error message
        message = self.get_deceptive_error(attack_type, input_snippet)
        
        # Set HTTP status code based on attack type
        http_status = 200
        if attack_type == AttackType.SQLI:
            http_status = 500  # Internal Server Error for SQL errors
        elif attack_type == AttackType.SSI:
            http_status = 403  # Forbidden for SSI attempts
        elif attack_type == AttackType.BRUTE_FORCE:
            http_status = 401  # Unauthorized for auth failures
        elif attack_type == AttackType.XSS:
            http_status = 200  # Success to make attacker think it worked
        # BENIGN gets 200
        
        return DeceptionResponse(
            message=message,
            delay_applied=apply_delay,
            http_status=http_status
        )

deception_engine = DeceptionEngine()
