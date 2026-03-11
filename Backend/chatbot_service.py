"""
AI Chatbot Service with Gemini API and DuckDuckGo Search
Provides cybersecurity-focused conversational AI with internet search capabilities
"""

import httpx
from duckduckgo_search import DDGS
from typing import List, Dict, Optional
import json
from datetime import datetime

from llm_controller import LLMController
from config import settings

class CybersecurityChatbot:
    def __init__(self, api_key: str = None):
        """Initialize the chatbot with our uniform DeepSeek LLMController"""
        self.llm = LLMController(provider="deepseek")
        
        # System context for cybersecurity focus
        self.system_context = """You are a cybersecurity expert AI assistant integrated into the Chameleon Adaptive Deception System. 
Your role is to help security analysts understand threats, attacks, and security concepts.

Key responsibilities:
- Explain attack patterns and techniques
- Provide threat intelligence insights
- Help interpret security logs and alerts
- Suggest mitigation strategies
- Answer cybersecurity questions with accuracy
- Use web search when you need current threat intelligence or recent CVE information

Always be concise, accurate, and security-focused. If you're unsure, say so and suggest using web search for the latest information."""
        
        # Initialize chat history
        self.chat_history = []
        
    def search_web(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search DuckDuckGo for cybersecurity information"""
        try:
            # Add cybersecurity context to search
            search_query = f"cybersecurity {query}"
            
            with DDGS() as ddgs:
                results = []
                for result in ddgs.text(search_query, max_results=max_results):
                    results.append({
                        'title': result.get('title', ''),
                        'snippet': result.get('body', ''),
                        'url': result.get('href', ''),
                    })
                return results
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def format_search_results(self, results: List[Dict]) -> str:
        """Format search results for the AI"""
        if not results:
            return "No search results found."
        
        formatted = "Web Search Results:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['title']}\n"
            formatted += f"   {result['snippet']}\n"
            formatted += f"   Source: {result['url']}\n\n"
        
        return formatted
    
    async def chat(
        self, 
        message: str, 
        use_search: bool = False,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Process a chat message and return response
        
        Args:
            message: User's message
            use_search: Whether to search the web for information
            context: Optional context (e.g., current attack logs, threat scores)
        """
        try:
            # Build the prompt
            prompt_parts = [self.system_context]
            
            # Add context if provided
            if context:
                prompt_parts.append(f"\nCurrent System Context:\n{json.dumps(context, indent=2)}")
            
            # Perform web search if requested
            search_results = []
            if use_search:
                search_results = self.search_web(message)
                if search_results:
                    prompt_parts.append(f"\n{self.format_search_results(search_results)}")
            
            # Add user message
            prompt_parts.append(f"\nUser Question: {message}")
            
            # Generate response
            full_prompt = "\n".join(prompt_parts)
            
            # Since LLMController expects standard API schemas, we wrap it in a pseudo-session prompt
            response_text = await self.llm.call_llm_api(full_prompt, system_prompt=self.system_context)
            
            # Store in history
            chat_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'user_message': message,
                'bot_response': response_text,
                'used_search': use_search,
                'search_results_count': len(search_results)
            }
            self.chat_history.append(chat_entry)
            
            return {
                'success': True,
                'response': response_text,
                'search_results': search_results if use_search else [],
                'timestamp': chat_entry['timestamp']
            }
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            print(error_msg)
            return {
                'success': False,
                'response': "I apologize, but I encountered an error processing your request. Please try again.",
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_chat_history(self, limit: int = 50) -> List[Dict]:
        """Get recent chat history"""
        return self.chat_history[-limit:]
    
    def clear_history(self):
        """Clear chat history"""
        self.chat_history = []
    
    async def analyze_attack(self, attack_data: Dict) -> str:
        """Analyze an attack log and provide insights"""
        prompt = f"""Analyze this security attack log and provide insights:

Attack Type: {attack_data.get('classification', {}).get('attack_type', 'Unknown')}
Confidence: {attack_data.get('classification', {}).get('confidence', 0)}
IP Address: {attack_data.get('ip_address', 'Unknown')}
Raw Input: {attack_data.get('raw_input', 'N/A')}
Timestamp: {attack_data.get('timestamp', 'Unknown')}

Provide:
1. Brief explanation of this attack type
2. Potential risks and impact
3. Recommended mitigation steps
4. Whether this appears to be automated or manual attack"""

        try:
            response_text = await self.llm.call_llm_api(prompt, system_prompt=self.system_context)
            return response_text
        except Exception as e:
            return f"Error analyzing attack: {str(e)}"
    
    async def suggest_response(self, threat_level: str, attack_type: str) -> str:
        """Suggest response actions based on threat level"""
        prompt = f"""As a cybersecurity expert, suggest immediate response actions for:

Threat Level: {threat_level}
Attack Type: {attack_type}

Provide:
1. Immediate actions to take
2. Investigation steps
3. Long-term preventive measures

Keep it concise and actionable."""

        try:
            response_text = await self.llm.call_llm_api(prompt, system_prompt=self.system_context)
            return response_text
        except Exception as e:
            return f"Error generating suggestions: {str(e)}"


# Global chatbot instance
_chatbot_instance: Optional[CybersecurityChatbot] = None

def get_chatbot(api_key: str = None) -> CybersecurityChatbot:
    """Get or create chatbot instance"""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = CybersecurityChatbot(api_key)
    return _chatbot_instance
