#!/bin/bash
echo "🔍 Monitoring Ornina AI Backend..."
echo "=================================="
echo ""
echo "Backend Process:"
ps aux | grep "agent.py dev" | grep -v grep
echo ""
echo "Configuration:"
grep -E "^TAVUS_API_KEY|^AVATAR_PROVIDER|^LIVEKIT_URL" .env
echo ""
echo "To see live activity, run in another terminal:"
echo "  cd /var/www/avatar\ /avatary"
echo "  python3 agent.py dev"
echo ""
echo "Press Ctrl+C to stop"
echo ""
echo "Waiting for LiveKit connections..."
echo "(Start a call from http://localhost:3000)"
