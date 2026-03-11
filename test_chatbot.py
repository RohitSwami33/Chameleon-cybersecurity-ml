#!/usr/bin/env python3
"""
Quick test script for the AI Chatbot functionality
"""

import asyncio
import sys
sys.path.insert(0, 'Backend')

from chatbot_service import CybersecurityChatbot

async def test_chatbot():
    print("🤖 Testing AI Chatbot Service\n")
    print("=" * 60)
    
    # Initialize chatbot
    api_key = "AIzaSyB7w5tQXvg1D7cVuqpeR6cZ5OMzNKCqguY"
    chatbot = CybersecurityChatbot(api_key)
    
    # Test 1: Basic question
    print("\n📝 Test 1: Basic Security Question")
    print("-" * 60)
    result = await chatbot.chat("What is SQL injection in one sentence?", use_search=False)
    if result['success']:
        print(f"✅ Response: {result['response'][:200]}...")
    else:
        print(f"❌ Error: {result.get('error')}")
    
    # Test 2: Web search
    print("\n🔍 Test 2: Web Search")
    print("-" * 60)
    search_results = chatbot.search_web("SQL injection prevention", max_results=3)
    if search_results:
        print(f"✅ Found {len(search_results)} results:")
        for i, result in enumerate(search_results, 1):
            print(f"   {i}. {result['title'][:60]}...")
    else:
        print("❌ No search results found")
    
    # Test 3: Chat with search
    print("\n🌐 Test 3: Chat with Web Search")
    print("-" * 60)
    result = await chatbot.chat("Latest ransomware threats", use_search=True)
    if result['success']:
        print(f"✅ Response: {result['response'][:200]}...")
        print(f"   Sources: {len(result['search_results'])} found")
    else:
        print(f"❌ Error: {result.get('error')}")
    
    # Test 4: Attack analysis
    print("\n🎯 Test 4: Attack Analysis")
    print("-" * 60)
    mock_attack = {
        'classification': {'attack_type': 'SQLI', 'confidence': 0.95},
        'ip_address': '192.168.1.100',
        'raw_input': "' OR 1=1--",
        'timestamp': '2025-11-22T23:40:00'
    }
    analysis = await chatbot.analyze_attack(mock_attack)
    print(f"✅ Analysis: {analysis[:200]}...")
    
    # Test 5: Response suggestions
    print("\n💡 Test 5: Response Suggestions")
    print("-" * 60)
    suggestions = await chatbot.suggest_response("CRITICAL", "SQLI")
    print(f"✅ Suggestions: {suggestions[:200]}...")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("\n📊 Chat History:")
    history = chatbot.get_chat_history()
    print(f"   Total messages: {len(history)}")

if __name__ == "__main__":
    asyncio.run(test_chatbot())
