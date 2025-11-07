#!/usr/bin/env python3
"""
Script to check Tavus API credits and account status
"""
import os
import asyncio
import aiohttp
import json
from dotenv import load_dotenv

load_dotenv()

async def check_credits():
    """Check Tavus account credits and usage"""
    api_key = os.environ.get("TAVUS_API_KEY")
    if not api_key:
        print("❌ TAVUS_API_KEY not found in environment variables")
        print("Please set TAVUS_API_KEY in your .env file")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        print("🔍 Checking Tavus account status...\n")
        
        # Check account info and credits
        try:
            async with session.get("https://api.tavus.io/v1/account") as response:
                if response.status == 200:
                    account_data = await response.json()
                    print("📊 Account Information:")
                    print(f"   Account ID: {account_data.get('account_id', 'N/A')}")
                    print(f"   Email: {account_data.get('email', 'N/A')}")
                    print(f"   Plan: {account_data.get('plan', 'N/A')}")
                    
                    # Check credits/usage if available
                    if 'credits' in account_data:
                        credits = account_data['credits']
                        print(f"\n💳 Credits Information:")
                        print(f"   Available Credits: {credits.get('available', 'N/A')}")
                        print(f"   Used Credits: {credits.get('used', 'N/A')}")
                        print(f"   Total Credits: {credits.get('total', 'N/A')}")
                        
                        available = credits.get('available', 0)
                        if available <= 0:
                            print("\n⚠️  WARNING: You are out of credits!")
                            print("   Please add more credits to continue using Tavus services.")
                        elif available < 10:
                            print(f"\n⚠️  WARNING: Low credits remaining ({available})")
                            print("   Consider adding more credits soon.")
                        else:
                            print(f"\n✅ Credits available: {available}")
                    
                    # Check usage statistics
                    if 'usage' in account_data:
                        usage = account_data['usage']
                        print(f"\n📈 Usage Statistics:")
                        print(f"   Conversations this month: {usage.get('conversations_this_month', 'N/A')}")
                        print(f"   Minutes this month: {usage.get('minutes_this_month', 'N/A')}")
                        print(f"   Total conversations: {usage.get('total_conversations', 'N/A')}")
                        print(f"   Total minutes: {usage.get('total_minutes', 'N/A')}")
                    
                elif response.status == 401:
                    print("❌ Authentication failed. Please check your TAVUS_API_KEY.")
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to get account info: {error_text}")
        
        except Exception as e:
            print(f"❌ Error checking account: {e}")
        
        # Check active conversations
        print("\n🔍 Checking active conversations...")
        try:
            async with session.get("https://api.tavus.io/v1/conversations") as response:
                if response.status == 200:
                    data = await response.json()
                    conversations = data.get("conversations", [])
                    
                    if not conversations:
                        print("✅ No active conversations found")
                    else:
                        print(f"Found {len(conversations)} active conversation(s):")
                        for conv in conversations:
                            conv_id = conv.get("conversation_id", "N/A")
                            status = conv.get("status", "unknown")
                            created_at = conv.get("created_at", "unknown")
                            replica_id = conv.get("replica_id", "N/A")
                            print(f"   ID: {conv_id}")
                            print(f"   Status: {status}")
                            print(f"   Replica ID: {replica_id}")
                            print(f"   Created: {created_at}")
                            print("   ---")
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to get conversations: {error_text}")
        
        except Exception as e:
            print(f"❌ Error checking conversations: {e}")
        
        # Check available replicas
        print("\n🔍 Checking available replicas...")
        try:
            async with session.get("https://api.tavus.io/v1/replicas") as response:
                if response.status == 200:
                    data = await response.json()
                    replicas = data.get("replicas", [])
                    
                    if not replicas:
                        print("❌ No replicas found")
                    else:
                        print(f"Found {len(replicas)} replica(s):")
                        for replica in replicas:
                            replica_id = replica.get("replica_id", "N/A")
                            name = replica.get("name", "N/A")
                            status = replica.get("status", "unknown")
                            print(f"   ID: {replica_id}")
                            print(f"   Name: {name}")
                            print(f"   Status: {status}")
                            print("   ---")
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to get replicas: {error_text}")
        
        except Exception as e:
            print(f"❌ Error checking replicas: {e}")

if __name__ == "__main__":
    asyncio.run(check_credits())
