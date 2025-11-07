#!/bin/bash

API_KEY="4d34762f06a646789b217cac11221253"

echo "🔍 Checking Tavus account status..."
echo

# Check account info
echo "📊 Account Information:"
response=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" "https://api.tavus.io/v1/account")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n -1)

if [ "$http_code" = "200" ]; then
    echo "✅ Successfully connected to Tavus API"
    echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
elif [ "$http_code" = "401" ]; then
    echo "❌ Authentication failed. Please check your TAVUS_API_KEY."
else
    echo "❌ Failed to get account info. HTTP Status: $http_code"
    echo "$body"
fi

echo

# Check active conversations
echo "🔍 Checking active conversations..."
response=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" "https://api.tavus.io/v1/conversations")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n -1)

if [ "$http_code" = "200" ]; then
    echo "$body" | python3 -m json.tool 2>/dev/null | grep -A 5 -B 5 "conversations" || echo "$body"
else
    echo "❌ Failed to get conversations. HTTP Status: $http_code"
    echo "$body"
fi

echo

# Check replicas
echo "🔍 Checking available replicas..."
response=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" "https://api.tavus.io/v1/replicas")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n -1)

if [ "$http_code" = "200" ]; then
    echo "$body" | python3 -m json.tool 2>/dev/null | grep -A 5 -B 5 "replicas" || echo "$body"
else
    echo "❌ Failed to get replicas. HTTP Status: $http_code"
    echo "$body"
fi
