import random
from models import AttackType, DeceptionResponse
from config import settings

class DeceptionEngine:
    def __init__(self):
        self.responses = {
            AttackType.SQLI: [
                "Error: You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '' at line 1",
                "Table 'users' doesn't exist",
                "Access denied for user 'root'@'localhost'",
                "Unclosed quotation mark after the character string"
            ],
            AttackType.XSS: [
                "Input validated successfully",
                "Form submitted. Thank you for your feedback.",
                "Profile updated.",
                "Comment added to queue for moderation."
            ],
            AttackType.SSI: [
                "Server-side includes are disabled on this server.",
                "Error: SSI directives not allowed in user input.",
                "Request processed. Server configuration prevents SSI execution.",
                "Input sanitized successfully."
            ],
            AttackType.BRUTE_FORCE: [
                "Invalid credentials. Please try again.",
                "Login failed. 2 attempts remaining.",
                "Account locked due to suspicious activity.",
                "Incorrect password."
            ],
            AttackType.BENIGN: [
                "Request processed successfully.",
                "Operation completed.",
                "Data retrieved.",
                "OK"
            ]
        }

    def generate_response(self, attack_type: AttackType, apply_delay: float) -> DeceptionResponse:
        message_list = self.responses.get(attack_type, self.responses[AttackType.BENIGN])
        message = random.choice(message_list)
        
        http_status = 200
        if attack_type == AttackType.SQLI:
            http_status = 500
        elif attack_type == AttackType.SSI:
            http_status = 403
        elif attack_type == AttackType.BRUTE_FORCE:
            http_status = 401
        # XSS and BENIGN get 200
        
        return DeceptionResponse(
            message=message,
            delay_applied=apply_delay,
            http_status=http_status
        )

deception_engine = DeceptionEngine()
