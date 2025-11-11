# Call Center System - Getting Started Guide

Welcome to the Call Center System! This guide will help you set up and run the complete system with both backend API and frontend interface.

---

## 📋 Prerequisites

Before starting, ensure you have:

- **Python 3.9+** - Download from https://www.python.org
- **Node.js 16+** - Download from https://nodejs.org
- **Git** (optional, for version control)
- **A terminal/command prompt**

### Check Installation

```bash
# Check Python version
python3 --version

# Check Node.js version
node --version

# Check npm version
npm --version
```

---

## 🚀 Quick Start (Recommended)

### On Linux/macOS

```bash
cd /var/www/avatar
chmod +x start-call-center.sh
./start-call-center.sh
```

### On Windows

```bash
cd \path\to\avatar
start-call-center.bat
```

The script will:
1. Set up Python virtual environment
2. Install Python dependencies
3. Set up Node.js packages
4. Start both backend API (port 8000) and frontend (port 3000)

---

## 📖 Manual Setup

### Step 1: Backend Setup

```bash
# Navigate to call center directory
cd /var/www/avatar/callCenter

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start Backend API

```bash
# From /var/www/avatar/callCenter directory with venv activated

# Option 1: Run main.py
python main.py

# Option 2: Use uvicorn directly
uvicorn api:app --reload

# Option 3: Specify port
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 3: Frontend Setup (New Terminal)

```bash
# Navigate to frontend directory
cd /var/www/avatar/frontend

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### Step 4: Start Frontend

```bash
# From /var/www/avatar/frontend directory

# Development mode
npm run dev

# Production build (if needed)
npm run build
npm start
```

**Expected output:**
```
> next dev
  ▲ Next.js 14.0.0
  - Ready in XXXms
  - Local: http://localhost:3000
```

---

## 🌐 Accessing the System

Once both services are running:

### Frontend
- **Main Page**: http://localhost:3000
- **Call Center Hub**: http://localhost:3000/callcenter
- **Start Call**: http://localhost:3000/callcenter/call
- **Agent Dashboard**: http://localhost:3000/callcenter/agent-dashboard
- **CRM Dashboard**: http://localhost:3000/callcenter/crm-dashboard

### Backend API
- **API Root**: http://localhost:8000
- **Interactive Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Documentation**: http://localhost:8000/redoc (ReDoc)
- **Health Check**: http://localhost:8000/health

### WebSocket
- **Real-time Updates**: ws://localhost:8000/ws/updates

---

## ✅ Verify Everything is Working

### Check API Status

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-11-08T12:00:00.000000",
  "active_calls": 0,
  "queued_calls": 0,
  "total_agents": 3
}
```

### Test a Simple API Call

```bash
# Create a new call
curl -X POST "http://localhost:8000/api/calls?phone_number=%2B966501234567&customer_name=John%20Doe"

# Get active calls
curl http://localhost:8000/api/calls

# Get agents
curl http://localhost:8000/api/agents
```

---

## 🔧 Configuration

### Backend Configuration

Edit `/var/www/avatar/callCenter/config.py` to customize:

- IVR prompts (Arabic/English)
- Department routing rules
- Ticket priority rules
- Customer support settings

### Frontend Configuration

Edit `/var/www/avatar/frontend/.env.local`:

```env
# API Server
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: For production
# NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

---

## 📁 Directory Structure

```
/var/www/avatar/
├── callCenter/                    # Backend API
│   ├── api.py                     # FastAPI application
│   ├── main.py                    # Entry point
│   ├── config.py                  # Configuration
│   ├── models.py                  # Data models
│   ├── call_router.py             # IVR routing
│   ├── crm_system.py              # CRM system
│   ├── rules_engine.py            # Rules engine
│   ├── prompts/                   # Department prompts
│   ├── utils/                     # Utilities
│   ├── database/                  # Database schema
│   ├── requirements.txt           # Python dependencies
│   └── venv/                      # Virtual environment
│
├── frontend/                      # Frontend UI
│   ├── pages/
│   │   ├── callcenter.tsx         # Main hub
│   │   └── callcenter/
│   │       ├── call.tsx           # Call interface
│   │       ├── agent-dashboard.tsx # Agent monitoring
│   │       └── crm-dashboard.tsx  # CRM interface
│   ├── components/                # React components
│   ├── hooks/
│   │   └── useCallCenterAPI.ts    # API hook
│   ├── package.json               # Node dependencies
│   ├── .env.local                 # Environment config
│   └── node_modules/              # Node packages
│
├── CALL_CENTER_FRONTEND_GUIDE.md
├── CALL_CENTER_API_INTEGRATION.md
└── start-call-center.sh           # Start script (Linux/macOS)
```

---

## 🎨 Using the Application

### For Customers (Call Interface)

1. Navigate to http://localhost:3000/callcenter
2. Click "Start Call"
3. Use the call interface to simulate a customer call
4. Send chat messages to the bot
5. View the call control buttons (mute, video, chat, end)

### For Agents (Agent Dashboard)

1. Navigate to http://localhost:3000/callcenter/agent-dashboard
2. View active calls in real-time
3. Monitor queue with waiting customers
4. Select a call to see details
5. Use buttons to hold, transfer, or end calls

### For CRM (Ticket Management)

1. Navigate to http://localhost:3000/callcenter/crm-dashboard
2. Switch between Tickets and Customers tabs
3. Select a ticket to view details
4. Edit or mark tickets as resolved
5. View customer interaction history

---

## 🧪 Testing with Sample Data

The system comes with pre-populated sample data:

### Sample Agents
- **AGT-001**: علي محمود (Reception)
- **AGT-002**: سارة أحمد (Sales)
- **AGT-003**: محمود علي (Complaints)

### Sample API Tests

```bash
# Get all agents
curl http://localhost:8000/api/agents

# Create a new ticket
curl -X POST "http://localhost:8000/api/tickets?customer_name=Ahmed&customer_phone=%2B966501234567&subject=Help&description=I%20need%20help&priority=high"

# Get all tickets
curl http://localhost:8000/api/tickets

# Update agent status
curl -X PATCH "http://localhost:8000/api/agents/AGT-001/status?status=busy"
```

---

## 📡 API Endpoints Quick Reference

### Calls
- `POST /api/calls` - Create new call
- `GET /api/calls` - List active calls
- `GET /api/calls/{id}` - Get call details
- `POST /api/calls/{id}/status` - Update status
- `POST /api/calls/{id}/route` - Route to department
- `POST /api/calls/{id}/transfer` - Transfer call
- `POST /api/calls/{id}/end` - End call
- `GET /api/calls/queue` - Get queued calls

### Tickets
- `POST /api/tickets` - Create ticket
- `GET /api/tickets` - List tickets
- `GET /api/tickets/{id}` - Get ticket
- `PATCH /api/tickets/{id}` - Update ticket

### Customers
- `GET /api/customers` - List customers
- `GET /api/customers/{id}` - Get customer

### Agents
- `GET /api/agents` - List agents
- `GET /api/agents/{id}` - Get agent
- `PATCH /api/agents/{id}/status` - Update status

### Transcripts
- `GET /api/transcripts/{call_id}` - Get transcript
- `POST /api/transcripts/{call_id}/messages` - Add message

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check Python version
python3 --version  # Must be 3.9+

# Check if port 8000 is in use
lsof -i :8000  # Linux/macOS

# Kill existing process
kill -9 <PID>  # Linux/macOS
taskkill /PID <PID> /F  # Windows

# Try with different port
uvicorn api:app --port 8001
```

### Frontend won't start

```bash
# Check Node.js version
node --version  # Must be 16+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Try with different port
npm run dev -- -p 3001
```

### WebSocket connection issues

```bash
# Check if backend is running
curl http://localhost:8000/health

# Test WebSocket connection
# Open browser console and run:
const ws = new WebSocket('ws://localhost:8000/ws/updates');
ws.onopen = () => console.log('Connected!');
ws.onerror = (e) => console.error('Error:', e);
```

### API requests return CORS errors

The API already has CORS enabled. If you get CORS errors:
1. Ensure API is running on port 8000
2. Check `.env.local` has correct API URL
3. Check browser console for more details

---

## 📚 Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Test the UI**: Try all three dashboards
3. **Read Documentation**: Check the markdown files in the root directory
4. **Configure Settings**: Customize in `config.py`
5. **Connect to Database**: Replace in-memory storage with PostgreSQL
6. **Add Authentication**: Implement user login and roles
7. **Deploy**: Use Docker for production deployment

---

## 📖 Documentation Files

- **CALL_CENTER_FRONTEND_GUIDE.md** - Frontend pages and components
- **CALL_CENTER_API_INTEGRATION.md** - API endpoints and integration examples
- **CALL_CENTER_IMPLEMENTATION_GUIDE.md** - Complete technical reference
- **CALL_CENTER_QUICK_START.md** - Quick reference guide

---

## 💡 Tips

- **Keep both terminals visible**: One for backend, one for frontend
- **Use browser DevTools**: Check Network tab for API calls, Console for errors
- **API Documentation is helpful**: http://localhost:8000/docs has all endpoints
- **Sample data resets on restart**: Backend uses in-memory storage
- **Check logs**: Look at terminal output for error messages

---

## 🆘 Getting Help

1. **Check the documentation**: Read the markdown files
2. **Review API docs**: http://localhost:8000/docs
3. **Check browser console**: Press F12 to open DevTools
4. **Review terminal logs**: Check for error messages
5. **Verify services are running**:
   - API: curl http://localhost:8000/health
   - Frontend: Visit http://localhost:3000

---

## 🎉 You're Ready!

Your Call Center System is now set up and running. Start with the Call Center Hub at http://localhost:3000/callcenter and explore the three modes:
- **Start Call** - Test customer interface
- **Agent Dashboard** - Monitor active calls
- **CRM Dashboard** - Manage tickets

Happy testing! 🚀
