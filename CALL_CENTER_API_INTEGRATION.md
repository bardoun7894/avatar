# Call Center API Integration Guide

## Overview

The Call Center system consists of:
- **Backend API**: FastAPI server running on port 8000
- **Frontend**: Next.js application running on port 3000
- **Real-time Updates**: WebSocket connection for live updates

---

## Backend Setup

### Installation

```bash
# Navigate to call center directory
cd /var/www/avatar/callCenter

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the API Server

```bash
# Option 1: Direct run
python main.py

# Option 2: Using uvicorn directly
uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# Option 3: Using Docker
docker build -f ../Dockerfile.backend -t call-center-api .
docker run -p 8000:8000 call-center-api
```

### API Documentation

Once running, access:
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)

---

## Frontend Setup

### Installation

```bash
cd /var/www/avatar/frontend

# Install dependencies
npm install

# Make sure Framer Motion is installed
npm install framer-motion
```

### Environment Configuration

Create `.env.local`:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Configure for production
# NEXT_PUBLIC_API_URL=https://api.example.com
```

### Running the Frontend

```bash
# Development server
npm run dev
# Server runs on http://localhost:3000

# Production build
npm run build
npm start
```

---

## API Endpoints

### Call Management

#### Initiate Call
```bash
POST /api/calls?phone_number=+966501234567&customer_name=John%20Doe
```

Response:
```json
{
  "success": true,
  "call_id": "CALL-A1B2C3D4",
  "call": {
    "call_id": "CALL-A1B2C3D4",
    "status": "initiated",
    "phone_number": "+966501234567",
    "customer_name": "John Doe",
    "started_at": "2024-11-08T12:00:00"
  }
}
```

#### Get Active Calls
```bash
GET /api/calls
GET /api/calls?status=in_progress
```

#### Update Call Status
```bash
POST /api/calls/CALL-001/status?status=in_progress
```

#### Route Call to Department
```bash
POST /api/calls/CALL-001/route?department=sales
```

#### Transfer Call
```bash
POST /api/calls/CALL-001/transfer?target_department=complaints&agent_id=AGT-003
```

#### End Call
```bash
POST /api/calls/CALL-001/end
```

#### Get Queue
```bash
GET /api/calls/queue
```

### Ticket Management (CRM)

#### Create Ticket
```bash
POST /api/tickets?customer_name=Ahmed%20Mohamed&customer_phone=%2B966501234567&subject=Delivery%20Issue&description=Package%20not%20received&priority=high&department=complaints
```

#### Get Tickets
```bash
GET /api/tickets
GET /api/tickets?status=open&priority=high
GET /api/tickets?department=complaints
```

#### Get Single Ticket
```bash
GET /api/tickets/TKT-20241108-0001
```

#### Update Ticket
```bash
PATCH /api/tickets/TKT-20241108-0001?status=resolved&notes=Issue%20resolved
PATCH /api/tickets/TKT-20241108-0001?assigned_to=AGT-002&priority=urgent
```

### Customer Management

#### Get All Customers
```bash
GET /api/customers
```

#### Get Customer Details
```bash
GET /api/customers/CUST-001
```

### Agent Management

#### Get Agents
```bash
GET /api/agents
GET /api/agents?status=available
```

#### Get Agent Details
```bash
GET /api/agents/AGT-001
```

#### Update Agent Status
```bash
PATCH /api/agents/AGT-001/status?status=busy
PATCH /api/agents/AGT-001/status?status=available
PATCH /api/agents/AGT-001/status?status=on_break
```

### Transcript Management

#### Get Transcript
```bash
GET /api/transcripts/CALL-001
```

#### Add Message to Transcript
```bash
POST /api/transcripts/CALL-001/messages?speaker=bot&content=Welcome%20to%20customer%20support&language=en
POST /api/transcripts/CALL-001/messages?speaker=customer&content=Hello%20I%20have%20a%20problem&language=ar
```

---

## WebSocket Real-Time Updates

### Connection

```javascript
// JavaScript
const ws = new WebSocket('ws://localhost:8000/ws/updates');

ws.onopen = () => {
  console.log('Connected');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

### React Hook

```typescript
import { useCallCenterAPI } from '@/hooks/useCallCenterAPI';

function MyComponent() {
  const { connectWebSocket, wsConnected } = useCallCenterAPI();

  useEffect(() => {
    connectWebSocket((message) => {
      console.log('Real-time update:', message);
      // Handle update based on message.type
    });
  }, [connectWebSocket]);

  return <div>Connected: {wsConnected ? 'Yes' : 'No'}</div>;
}
```

### Event Types

#### Call Events
```javascript
// New call added
{
  "type": "call:new",
  "data": { "call_id": "CALL-001", "customer_name": "Ahmed", ... }
}

// Call status updated
{
  "type": "call:updated",
  "data": { "call_id": "CALL-001", "status": "in_progress" }
}

// Call routed to department
{
  "type": "call:routed",
  "data": { "call_id": "CALL-001", "department": "sales" }
}

// Call transferred
{
  "type": "call:transferred",
  "data": { "call_id": "CALL-001", "to_department": "complaints", "to_agent": "AGT-003" }
}

// Call ended
{
  "type": "call:ended",
  "data": { "call_id": "CALL-001", "duration": 240 }
}
```

#### Ticket Events
```javascript
// New ticket created
{
  "type": "ticket:created",
  "data": { "ticket_id": "TKT-001", "customer_name": "Ahmed", ... }
}

// Ticket updated
{
  "type": "ticket:updated",
  "data": { "ticket_id": "TKT-001", "status": "resolved" }
}
```

#### Message Events
```javascript
// New chat message
{
  "type": "message:new",
  "data": { "call_id": "CALL-001", "speaker": "customer", "content": "Hello" }
}
```

#### Agent Events
```javascript
// Agent status changed
{
  "type": "agent:status_changed",
  "data": { "agent_id": "AGT-001", "status": "busy" }
}
```

---

## Using the React Hook

### Basic Usage

```typescript
import { useCallCenterAPI } from '@/hooks/useCallCenterAPI';

function CallPage() {
  const api = useCallCenterAPI();
  const [callId, setCallId] = useState<string | null>(null);

  const handleStartCall = async () => {
    const result = await api.initiatecall('+966501234567', 'Ahmed Mohamed');
    if (result) {
      setCallId(result.call_id);
    }
  };

  const handleEndCall = async () => {
    if (callId) {
      await api.endCall(callId);
    }
  };

  return (
    <div>
      {api.loading && <p>Loading...</p>}
      {api.error && <p>Error: {api.error}</p>}
      <button onClick={handleStartCall}>Start Call</button>
      <button onClick={handleEndCall} disabled={!callId}>
        End Call
      </button>
    </div>
  );
}
```

### Full Example with WebSocket

```typescript
import { useCallCenterAPI } from '@/hooks/useCallCenterAPI';
import { useEffect, useState } from 'react';

function AgentDashboard() {
  const api = useCallCenterAPI();
  const [calls, setCalls] = useState([]);

  useEffect(() => {
    // Load initial calls
    const loadCalls = async () => {
      const result = await api.getActivecalls();
      if (result) {
        setCalls(result.calls);
      }
    };

    loadCalls();

    // Connect to real-time updates
    api.connectWebSocket((message) => {
      switch (message.type) {
        case 'call:new':
          setCalls((prev) => [...prev, message.data]);
          break;
        case 'call:updated':
          setCalls((prev) =>
            prev.map((call) =>
              call.call_id === message.data.call_id
                ? { ...call, ...message.data }
                : call
            )
          );
          break;
        case 'call:ended':
          setCalls((prev) =>
            prev.filter((call) => call.call_id !== message.data.call_id)
          );
          break;
      }
    });
  }, [api]);

  return (
    <div>
      <p>Active Calls: {calls.length}</p>
      <p>WebSocket: {api.wsConnected ? 'Connected' : 'Disconnected'}</p>
      {calls.map((call) => (
        <div key={call.call_id}>
          <p>{call.customer_name} - {call.status}</p>
        </div>
      ))}
    </div>
  );
}
```

---

## Frontend Integration Examples

### Call Page (`pages/callcenter/call.tsx`)

```typescript
import { useCallCenterAPI } from '@/hooks/useCallCenterAPI'

export default function CallPage() {
  const api = useCallCenterAPI()
  const [callId, setCallId] = useState<string | null>(null)
  const [transcript, setTranscript] = useState<any[]>([])

  useEffect(() => {
    // Initialize call
    const initCall = async () => {
      const result = await api.initiatecall('+966501234567', 'Ahmed Mohamed')
      if (result) {
        setCallId(result.call_id)
      }
    }

    initCall()
  }, [api])

  const handleSendMessage = async (message: string) => {
    if (!callId) return

    // Add to transcript
    await api.addTranscriptMessage(callId, 'customer', message, 'ar')

    // Update UI
    setTranscript(prev => [...prev, { speaker: 'customer', content: message }])
  }

  return (
    // ... UI code
  )
}
```

### Agent Dashboard (`pages/callcenter/agent-dashboard.tsx`)

```typescript
import { useCallCenterAPI } from '@/hooks/useCallCenterAPI'

export default function AgentDashboard() {
  const api = useCallCenterAPI()
  const [activeCalls, setActiveCalls] = useState([])

  useEffect(() => {
    // Load active calls
    const loadCalls = async () => {
      const result = await api.getActivecalls('in_progress')
      if (result) {
        setActiveCalls(result.calls)
      }
    }

    loadCalls()

    // Connect to real-time updates
    api.connectWebSocket((message) => {
      if (message.type === 'call:updated') {
        setActiveCalls(prev =>
          prev.map(c => c.call_id === message.data.call_id ? { ...c, ...message.data } : c)
        )
      }
    })

    return () => api.disconnectWebSocket()
  }, [api])

  const handleTransferCall = async (callId: string, department: string) => {
    await api.transferCall(callId, department)
  }

  return (
    // ... UI code
  )
}
```

### CRM Dashboard (`pages/callcenter/crm-dashboard.tsx`)

```typescript
import { useCallCenterAPI } from '@/hooks/useCallCenterAPI'

export default function CRMDashboard() {
  const api = useCallCenterAPI()
  const [tickets, setTickets] = useState([])

  useEffect(() => {
    const loadTickets = async () => {
      const result = await api.getTickets('open')
      if (result) {
        setTickets(result.tickets)
      }
    }

    loadTickets()

    api.connectWebSocket((message) => {
      if (message.type === 'ticket:created') {
        setTickets(prev => [...prev, message.data])
      } else if (message.type === 'ticket:updated') {
        setTickets(prev =>
          prev.map(t => t.ticket_id === message.data.ticket_id ? { ...t, ...message.data } : t)
        )
      }
    })

    return () => api.disconnectWebSocket()
  }, [api])

  const handleResolveTicket = async (ticketId: string) => {
    await api.updateTicket(ticketId, { status: 'resolved' })
  }

  return (
    // ... UI code
  )
}
```

---

## Docker Deployment

### Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY callCenter/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY callCenter /app

EXPOSE 8000

CMD ["python", "main.py"]
```

### Frontend Dockerfile

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend .

EXPOSE 3000

CMD ["npm", "run", "dev"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./callCenter:/app

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: call_center
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - ./callCenter/database/schema.sql:/docker-entrypoint-initdb.d/init.sql
```

---

## Production Checklist

- [ ] Replace in-memory state with PostgreSQL database
- [ ] Add authentication and authorization
- [ ] Configure HTTPS/WSS for secure connections
- [ ] Set up environment variables from `.env` file
- [ ] Configure CORS for production domain
- [ ] Add rate limiting and request validation
- [ ] Implement proper error logging and monitoring
- [ ] Set up database backups
- [ ] Configure load balancing for API
- [ ] Add API request metrics and analytics

---

## Troubleshooting

### WebSocket Connection Failed

**Problem**: WebSocket connects to wrong port
**Solution**: Ensure API is running on port 8000. Check network settings and firewall.

```javascript
// Debug WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/updates');
console.log('WebSocket state:', ws.readyState);
```

### CORS Errors

**Problem**: Frontend can't access API
**Solution**: API already has CORS enabled for all origins. Check API is running.

```bash
# Verify API is running
curl http://localhost:8000/health
```

### Missing Dependencies

**Problem**: `ModuleNotFoundError` when running API
**Solution**: Install requirements

```bash
pip install -r callCenter/requirements.txt
```

---

## Support

For issues or questions:
1. Check API documentation at http://localhost:8000/docs
2. Review error messages in console and logs
3. Verify API and frontend ports (8000 and 3000)
4. Ensure all dependencies are installed
5. Check environment configuration

