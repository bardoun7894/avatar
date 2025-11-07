#!/bin/bash
echo "🎥 Monitoring Vision System..."
echo "================================"
echo ""
tail -f agent_vision_live.log | grep --line-buffered -E "Monitoring|video|track|Vision|👁️|📹|🎥|entrypoint"
