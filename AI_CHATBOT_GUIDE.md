# AI Chatbot Integration Guide

## Overview
The Chameleon Adaptive Deception System now includes an AI-powered cybersecurity assistant that helps security analysts understand threats, analyze attacks, and get real-time threat intelligence.

## Features

### 🤖 AI-Powered Responses
- **Gemini AI Integration**: Uses Google's Gemini Pro model for intelligent, context-aware responses
- **Cybersecurity Focus**: Trained to provide expert-level security insights
- **Natural Conversations**: Maintains chat history for contextual understanding

### 🔍 Web Search Capabilities
- **DuckDuckGo Integration**: Search the internet for current threat intelligence
- **Real-time Information**: Get the latest CVE details, security advisories, and threat reports
- **Source Citations**: All search results include source URLs for verification

### 💡 Smart Features
1. **Quick Questions**: Pre-defined questions for common security topics
2. **Attack Analysis**: AI-powered analysis of specific attack logs
3. **Response Suggestions**: Get recommended actions based on threat levels
4. **Copy to Clipboard**: Easy copying of AI responses
5. **Chat History**: Persistent conversation history during session

## API Endpoints

### 1. Chat with Bot
```http
POST /api/chatbot/chat
Authorization: Bearer <token>

{
  "message": "What is SQL injection?",
  "use_search": false,
  "context": {}
}
```

**Response:**
```json
{
  "success": true,
  "response": "SQL injection is a code injection technique...",
  "search_results": [],
  "timestamp": "2025-11-22T23:40:00.000Z"
}
```

### 2. Get Chat History
```http
GET /api/chatbot/history?limit=50
Authorization: Bearer <token>
```

### 3. Clear Chat History
```http
POST /api/chatbot/clear-history
Authorization: Bearer <token>
```

### 4. Analyze Attack with AI
```http
POST /api/chatbot/analyze-attack/{log_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "log_id": "abc123",
  "analysis": "This SQL injection attempt shows...",
  "timestamp": "2025-11-22T23:40:00.000Z"
}
```

### 5. Get Response Suggestions
```http
POST /api/chatbot/suggest-response
Authorization: Bearer <token>

{
  "threat_level": "CRITICAL",
  "attack_type": "SQLI"
}
```

### 6. Search Cybersecurity Info
```http
POST /api/chatbot/search?query=latest ransomware&max_results=5
Authorization: Bearer <token>
```

## Configuration

### Backend Setup
The Gemini API key is configured in `Backend/config.py`:

```python
GEMINI_API_KEY: str = "AIzaSyB7w5tQXvg1D7cVuqpeR6cZ5OMzNKCqguY"
```

**Security Note**: In production, move this to environment variables:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

### Dependencies
Added to `Backend/requirements.txt`:
```
google-generativeai==0.3.2    # Google Gemini API
duckduckgo-search==4.1.1      # DuckDuckGo search
```

## Usage Examples

### Example 1: Basic Question
**User**: "What is XSS?"
**Bot**: Provides detailed explanation of Cross-Site Scripting attacks

### Example 2: With Web Search
**User**: "Latest CVE vulnerabilities in Apache" (with search enabled)
**Bot**: Searches DuckDuckGo and provides current information with sources

### Example 3: Attack Analysis
**User**: Clicks "Analyze with AI" on an attack log
**Bot**: Provides detailed analysis including:
- Attack type explanation
- Risk assessment
- Mitigation recommendations
- Attack pattern identification

### Example 4: Quick Questions
Pre-defined questions available:
- "What is SQL injection?"
- "Explain XSS attacks"
- "How to prevent brute force attacks?"
- "Latest cybersecurity threats"
- "What is a honeypot?"

## UI Features

### Chat Interface
- **Modern Design**: Gradient purple theme matching the dashboard
- **Message Bubbles**: Clear distinction between user and bot messages
- **Timestamps**: All messages include timestamps
- **Loading Indicators**: Shows when AI is thinking
- **Error Handling**: Graceful error messages

### Controls
- **Web Search Toggle**: Enable/disable internet search
- **Clear History**: Reset conversation
- **Copy Button**: Copy bot responses to clipboard
- **Quick Questions**: One-click common questions

### Search Results Display
When web search is enabled:
- Shows top 3 sources inline
- Clickable links to original sources
- Snippet previews
- Source count indicator

## Best Practices

### 1. When to Use Web Search
- ✅ Latest CVE information
- ✅ Current threat intelligence
- ✅ Recent security advisories
- ✅ Emerging attack patterns
- ❌ General security concepts (AI knowledge is sufficient)

### 2. Effective Questions
**Good:**
- "Analyze this SQL injection pattern: ' OR 1=1--"
- "What are the latest ransomware trends?"
- "How should I respond to a CRITICAL threat from IP 192.168.1.100?"

**Less Effective:**
- "Help" (too vague)
- "What is security?" (too broad)

### 3. Context Usage
The chatbot can use system context:
```javascript
{
  message: "Should I be concerned about this IP?",
  context: {
    ip: "192.168.1.100",
    threat_score: 85,
    attack_count: 15
  }
}
```

## Security Considerations

1. **API Key Protection**: Store Gemini API key in environment variables
2. **Rate Limiting**: Consider implementing rate limits for API calls
3. **Input Validation**: All user inputs are validated before processing
4. **Authentication**: All endpoints require valid JWT token
5. **Search Safety**: DuckDuckGo searches are prefixed with "cybersecurity" context

## Troubleshooting

### Issue: "Failed to get response from AI assistant"
**Solution**: Check Gemini API key is valid and has quota remaining

### Issue: No search results
**Solution**: 
- Check internet connectivity
- Verify DuckDuckGo is accessible
- Try different search terms

### Issue: Slow responses
**Solution**:
- Disable web search for faster responses
- Check API rate limits
- Verify network latency

## Future Enhancements

Potential improvements:
1. **Multi-language Support**: Support for multiple languages
2. **Voice Input**: Speech-to-text for hands-free operation
3. **Export Conversations**: Download chat history as PDF
4. **Custom Training**: Fine-tune on organization-specific threats
5. **Integration with SIEM**: Direct integration with security tools
6. **Automated Alerts**: AI-triggered alerts for critical threats

## API Limits

### Gemini API
- Free tier: 60 requests per minute
- Consider upgrading for production use

### DuckDuckGo
- No official rate limits
- Implement reasonable delays between searches

## Support

For issues or questions:
1. Check backend logs: `tail -f backend.log`
2. Verify API key configuration
3. Test endpoints with curl
4. Check browser console for frontend errors

## Example Integration

```javascript
// Frontend usage example
import api from '../services/api';

const response = await api.post('/chatbot/chat', {
  message: 'Explain this attack',
  use_search: true,
  context: {
    attack_type: 'SQLI',
    confidence: 0.95
  }
});

console.log(response.data.response);
```

---

**Version**: 1.0.0  
**Last Updated**: November 22, 2025  
**Powered by**: Google Gemini AI + DuckDuckGo Search
