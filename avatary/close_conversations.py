#!/usr/bin/env python3
"""
Script to check and close active Tavus conversations
"""
import os
import asyncio
import aiohttp
import json
from dotenv import load_dotenv

load_dotenv()

async def check_conversations():
    """Check active conversations"""
    api_key = os.environ.get("TAVUS_API_KEY")
    if not api_key:
        print("❌ TAVUS_API_KEY not found in environment variables")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        # Get conversations
        try:
            async with session.get("https://api.tavus.io/v1/conversations") as response:
                if response.status == 200:
                    data = await response.json()
                    conversations = data.get("conversations", [])
                    
                    if not conversations:
                        print("✅ No active conversations found")
                        return
                    
                    print(f"Found {len(conversations)} conversation(s):")
                    for conv in conversations:
                        conv_id = conv.get("conversation_id")
                        status = conv.get("status", "unknown")
                        created_at = conv.get("created_at", "unknown")
                        print(f"  ID: {conv_id}, Status: {status}, Created: {created_at}")
                        
                        # Close the conversation
                        if status in ["active", "in_progress"]:
                            print(f"  Closing conversation {conv_id}...")
                            try:
                                async with session.patch(
                                    f"https://api.tavus.io/v1/conversations/{conv_id}",
                                    json={"status": "completed"}
                                ) as close_response:
                                    if close_response.status == 200:
                                        print(f"  ✅ Successfully closed conversation {conv_id}")
                                    else:
                                        error_text = await close_response.text()
                                        print(f"  ❌ Failed to close conversation {conv_id}: {error_text}")
                            except Exception as e:
                                print(f"  ❌ Error closing conversation {conv_id}: {e}")
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to get conversations: {error_text}")
        except Exception as e:
            print(f"❌ Error checking conversations: {e}")

if __name__ == "__main__":
    asyncio.run(check_conversations())
