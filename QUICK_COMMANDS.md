# Quick Command Reference

## Start the System

### Option 1: Automatic (Recommended)
```bash
cd /var/www/avatar && chmod +x start-call-center.sh && ./start-call-center.sh
```

### Option 2: Manual Backend
```bash
cd /var/www/avatar/callCenter
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Option 3: Manual Frontend
```bash
cd /var/www/avatar/frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

---

## API Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Create Call
```bash
curl -X POST "http://localhost:8000/api/calls?phone_number=%2B966501234567&customer_name=Ahmed%20Mohamed"
```

### Get Active Calls
```bash
curl http://localhost:8000/api/calls
```

### Create Ticket
```bash
curl -X POST "http://localhost:8000/api/tickets?customer_name=Ahmed&customer_phone=%2B966501234567&subject=Help&description=Issue&priority=high"
```

### Get Tickets
```bash
curl http://localhost:8000/api/tickets
```

### Get Agents
```bash
curl http://localhost:8000/api/agents
```

### Update Agent Status
```bash
curl -X PATCH "http://localhost:8000/api/agents/AGT-001/status?status=busy"
```

---

## Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Call Center Hub | http://localhost:3000/callcenter |
| Start Call | http://localhost:3000/callcenter/call |
| Agent Dashboard | http://localhost:3000/callcenter/agent-dashboard |
| CRM Dashboard | http://localhost:3000/callcenter/crm-dashboard |
| API Root | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (ReDoc) | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |
| WebSocket | ws://localhost:8000/ws/updates |

---

## Docker Commands

### Build Backend
```bash
docker build -f Dockerfile.backend -t call-center-api .
```

### Run Backend
```bash
docker run -p 8000:8000 call-center-api
```

### Build Frontend
```bash
docker build -f Dockerfile.frontend -t call-center-web .
```

### Run Frontend
```bash
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8000 call-center-web
```

### Docker Compose
```bash
docker-compose up -d
```

---

## Development Commands

### Backend (From /var/www/avatar/callCenter)

Activate Virtual Environment:
```bash
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate.bat  # Windows
```

Run API:
```bash
python main.py
# or
uvicorn api:app --reload
# or with custom port
uvicorn api:app --port 8001 --reload
```

Install Dependencies:
```bash
pip install -r requirements.txt
```

### Frontend (From /var/www/avatar/frontend)

Install Dependencies:
```bash
npm install
```

Development:
```bash
npm run dev
```

Production Build:
```bash
npm run build
npm start
```

---

## Troubleshooting

### Port Already in Use

Kill process on port 8000 (Backend):
```bash
# Linux/macOS
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

Kill process on port 3000 (Frontend):
```bash
# Linux/macOS
lsof -i :3000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Virtual Environment Issues

Remove and recreate:
```bash
cd /var/www/avatar/callCenter
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Dependencies Issues

```bash
# Clear cache and reinstall (Backend)
cd /var/www/avatar/callCenter
pip install --upgrade pip
pip install --force-reinstall -r requirements.txt

# Clear cache and reinstall (Frontend)
cd /var/www/avatar/frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### WebSocket Connection Issues

Check if backend is running:
```bash
curl http://localhost:8000/health
```

Test WebSocket in browser console:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/updates');
ws.onopen = () => console.log('Connected!');
ws.onerror = (e) => console.error('Error:', e);
ws.onmessage = (e) => console.log('Message:', e.data);
```

---

## Documentation Quick Links

- **Getting Started**: Read [CALL_CENTER_GETTING_STARTED.md](./CALL_CENTER_GETTING_STARTED.md)
- **API Reference**: Read [CALL_CENTER_API_INTEGRATION.md](./CALL_CENTER_API_INTEGRATION.md)
- **Complete Guide**: Read [CALL_CENTER_COMPLETE.md](./CALL_CENTER_COMPLETE.md)
- **Status Report**: Read [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md)
- **Interactive Docs**: Visit http://localhost:8000/docs (when running)

---

## Sample Data

### Default Agents
- **AGT-001**: علي محمود (Reception)
- **AGT-002**: سارة أحمد (Sales)
- **AGT-003**: محمود علي (Complaints)

### Sample Calls
- Automatically created when you use the API
- IDs format: CALL-XXXXXXXX

### Sample Tickets
- Automatically created when tickets are created via API
- IDs format: TKT-YYYYMMDD-XXXX

---

## Environment Variables

Create `.env.local` in `/var/www/avatar/frontend/`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production:
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

---

## File Locations

```
/var/www/avatar/
├── callCenter/
│   ├── api.py              (FastAPI app)
│   ├── main.py             (Entry point)
│   ├── requirements.txt    (Python deps)
│   ├── config.py           (Configuration)
│   ├── models.py           (Data models)
│   └── [other modules]
├── frontend/
│   ├── pages/              (React pages)
│   ├── hooks/              (React hooks)
│   ├── components/         (Components)
│   ├── package.json        (Node deps)
│   └── [other files]
├── start-call-center.sh    (Linux/macOS)
├── start-call-center.bat   (Windows)
└── [documentation files]
```

---

## Performance Tips

1. **Use WebSocket for real-time updates** instead of polling
2. **Implement caching** for frequently accessed data
3. **Use connection pooling** for database
4. **Enable compression** in production
5. **Use CDN** for static assets
6. **Monitor API response times** regularly
7. **Implement rate limiting** to prevent abuse

---

## Next Steps

1. Run `./start-call-center.sh`
2. Visit http://localhost:3000/callcenter
3. Explore the three modes (Call, Agent Dashboard, CRM)
4. Visit http://localhost:8000/docs for API documentation
5. Read CALL_CENTER_GETTING_STARTED.md for detailed setup

---

**Last Updated**: November 8, 2025
**Version**: 1.0.0
