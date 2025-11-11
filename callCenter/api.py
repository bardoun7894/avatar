#!/usr/bin/env python3
"""
Call Center FastAPI Application
Exposes call center functionality as REST and WebSocket endpoints
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

# Import call center modules using absolute imports
# Docker runs with all files in /app, so absolute imports work
from models import (
    Call, Ticket, Agent, CustomerProfile, CallTranscript,
    CallStatus, Department, TicketStatus, TicketPriority,
    AgentStatus, IVRStage, CallDirection, TranscriptMessage
)
from call_router import CallRouter
from crm_system import CRMSystem
from rules_engine import RulesEngine
from config import CallCenterConfig
from conversation_api import router as conversation_router
from openai_personas import get_persona_manager
from audio_handler import create_audio_endpoints
from livekit_endpoints import register_livekit_endpoints

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# GLOBAL STATE MANAGEMENT
# ============================================================================

class CallCenterState:
    """In-memory storage for call center data (replace with DB for production)"""

    def __init__(self):
        self.active_calls: Dict[str, Call] = {}
        self.tickets: Dict[str, Ticket] = {}
        self.agents: Dict[str, Agent] = {}
        self.customers: Dict[str, CustomerProfile] = {}
        self.transcripts: Dict[str, CallTranscript] = {}
        self.queue: List[str] = []  # call_ids in queue
        self.websocket_connections: Dict[str, WebSocket] = {}

    def get_active_calls_count(self) -> int:
        """Get count of active calls"""
        return len([c for c in self.active_calls.values()
                   if c.status in [CallStatus.IN_PROGRESS, CallStatus.TRANSFERRED]])

    def get_queue_count(self) -> int:
        """Get count of queued calls"""
        return len(self.queue)


# Initialize state
state = CallCenterState()
config = CallCenterConfig()
rules_engine = RulesEngine()
call_router = CallRouter()
crm_system = CRMSystem()

# ============================================================================
# LIFESPAN EVENTS
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Call Center API starting up...")

    # Initialize sample agents
    sample_agents = [
        Agent(
            agent_id="AGT-001",
            name="علي محمود",
            email="ali@example.com",
            phone="+966501234567",
            department=Department.RECEPTION,
            skills=["greeting", "information"],
            status=AgentStatus.AVAILABLE
        ),
        Agent(
            agent_id="AGT-002",
            name="سارة أحمد",
            email="sarah@example.com",
            phone="+966502345678",
            department=Department.SALES,
            skills=["sales", "product_demo"],
            status=AgentStatus.AVAILABLE
        ),
        Agent(
            agent_id="AGT-003",
            name="محمود علي",
            email="mahmoud@example.com",
            phone="+966503456789",
            department=Department.COMPLAINTS,
            skills=["complaints", "escalation"],
            status=AgentStatus.AVAILABLE
        ),
    ]

    for agent in sample_agents:
        state.agents[agent.agent_id] = agent

    logger.info(f"Initialized {len(state.agents)} agents")

    # Register audio endpoints
    logger.info("Registering audio endpoints...")
    await create_audio_endpoints(app)
    logger.info("Audio endpoints registered successfully")

    # Register LiveKit endpoints for real-time audio communication
    logger.info("Registering LiveKit endpoints...")
    await register_livekit_endpoints(app)
    logger.info("LiveKit endpoints registered successfully")

    yield

    logger.info("Call Center API shutting down...")

# ============================================================================
# CREATE FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Call Center API",
    description="Complete call center system with IVR, CRM, and agent management",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# CONVERSATION COMPATIBILITY ENDPOINT (MUST BE BEFORE ROUTER INCLUSION)
# ============================================================================

class ConversationRequest(BaseModel):
    """Request model for conversation API"""
    message: str
    language: str = "ar"


@app.post("/api/conversation/{call_id}/send")
async def conversation_endpoint(call_id: str, request: ConversationRequest):
    """
    Compatibility endpoint for conversation requests
    """
    try:
        logger.info(f"📨 Received message for call {call_id}: {request.message}")
        response = {
            "text": f"شكراً لرسالتك: {request.message}. كيف يمكنني مساعدتك؟",
            "persona": "Customer Service",
            "audio_url": None,
            "timestamp": datetime.now().isoformat()
        }
        return response
    except Exception as e:
        logger.error(f"Error in conversation endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Conversation failed: {str(e)}"
        )


# Include conversation router
app.include_router(conversation_router)

# Audio endpoints will be registered via lifespan startup
# (endpoints are added to the app directly by the audio_handler module)

# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_calls": state.get_active_calls_count(),
        "queued_calls": state.get_queue_count(),
        "total_agents": len(state.agents),
    }

# ============================================================================
# CALL ENDPOINTS
# ============================================================================

@app.post("/api/calls")
async def initiate_call(
    phone_number: Optional[str] = Query(None),
    customer_name: Optional[str] = Query(None),
    direction: str = Query("inbound")
):
    """
    Initiate a new call

    Query Parameters:
    - phone_number: Customer phone number
    - customer_name: Customer name
    - direction: "inbound" or "outbound"

    Returns: Call object with assigned call_id
    """
    try:
        # Create new call
        call_id = f"CALL-{uuid4().hex[:8].upper()}"

        call = Call(
            call_id=call_id,
            phone_number=phone_number,
            customer_name=customer_name,
            direction=CallDirection(direction),
            status=CallStatus.INITIATED,
            ivr_stage=IVRStage.WELCOME
        )

        # Store call
        state.active_calls[call_id] = call

        # Create transcript
        transcript = CallTranscript(
            call_id=call_id,
            customer_name=customer_name,
            messages=[]
        )
        state.transcripts[call_id] = transcript

        logger.info(f"Call initiated: {call_id}")

        return {
            "success": True,
            "call_id": call_id,
            "call": call.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error initiating call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/calls")
async def get_active_calls(status: Optional[str] = Query(None)):
    """
    Get list of active calls

    Query Parameters:
    - status: Filter by status (optional)

    Returns: List of Call objects
    """
    try:
        calls = list(state.active_calls.values())

        if status:
            calls = [c for c in calls if c.status.value == status]

        return {
            "success": True,
            "count": len(calls),
            "calls": [c.model_dump() for c in calls],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching calls: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/calls/{call_id}")
async def get_call(call_id: str = Path(...)):
    """
    Get specific call details

    Path Parameters:
    - call_id: Call ID to retrieve

    Returns: Call object
    """
    if call_id not in state.active_calls:
        raise HTTPException(status_code=404, detail=f"Call {call_id} not found")

    try:
        call = state.active_calls[call_id]
        return {
            "success": True,
            "call": call.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching call {call_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/calls/{call_id}/status")
async def update_call_status(
    call_id: str = Path(...),
    status: str = Query(...)
):
    """
    Update call status

    Path Parameters:
    - call_id: Call ID to update

    Query Parameters:
    - status: New status (initiated, ivr_processing, in_queue, in_progress, transferred, completed, abandoned, failed)

    Returns: Updated Call object
    """
    if call_id not in state.active_calls:
        raise HTTPException(status_code=404, detail=f"Call {call_id} not found")

    try:
        call = state.active_calls[call_id]
        call.status = CallStatus(status)
        call.updated_at = datetime.now()

        logger.info(f"Call {call_id} status updated to {status}")

        # Broadcast update via WebSocket
        await broadcast_update("call:updated", {
            "call_id": call_id,
            "status": status
        })

        return {
            "success": True,
            "call": call.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid status: {str(e)}")
    except Exception as e:
        logger.error(f"Error updating call {call_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/calls/{call_id}/route")
async def route_call(
    call_id: str = Path(...),
    department: str = Query(...)
):
    """
    Route call to a specific department

    Path Parameters:
    - call_id: Call ID to route

    Query Parameters:
    - department: Target department (reception, sales, complaints)

    Returns: Updated Call object with assigned department
    """
    if call_id not in state.active_calls:
        raise HTTPException(status_code=404, detail=f"Call {call_id} not found")

    try:
        call = state.active_calls[call_id]
        call.department = Department(department)
        call.status = CallStatus.IN_QUEUE

        # Add to queue
        state.queue.append(call_id)

        logger.info(f"Call {call_id} routed to {department}")

        # Broadcast update
        await broadcast_update("call:routed", {
            "call_id": call_id,
            "department": department
        })

        return {
            "success": True,
            "call": call.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid department: {str(e)}")
    except Exception as e:
        logger.error(f"Error routing call {call_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/calls/{call_id}/transfer")
async def transfer_call(
    call_id: str = Path(...),
    target_department: str = Query(...),
    agent_id: Optional[str] = Query(None)
):
    """
    Transfer call to another department or agent

    Path Parameters:
    - call_id: Call ID to transfer

    Query Parameters:
    - target_department: Department to transfer to
    - agent_id: Specific agent to transfer to (optional)

    Returns: Updated Call object
    """
    if call_id not in state.active_calls:
        raise HTTPException(status_code=404, detail=f"Call {call_id} not found")

    try:
        call = state.active_calls[call_id]
        call.department = Department(target_department)
        call.status = CallStatus.TRANSFERRED
        if agent_id:
            call.assigned_agent_id = agent_id

        logger.info(f"Call {call_id} transferred to {target_department}")

        # Broadcast update
        await broadcast_update("call:transferred", {
            "call_id": call_id,
            "to_department": target_department,
            "to_agent": agent_id
        })

        return {
            "success": True,
            "call": call.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error transferring call {call_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/calls/{call_id}/end")
async def end_call(call_id: str = Path(...)):
    """
    End a call and mark as completed

    Path Parameters:
    - call_id: Call ID to end

    Returns: Completed Call object
    """
    if call_id not in state.active_calls:
        raise HTTPException(status_code=404, detail=f"Call {call_id} not found")

    try:
        call = state.active_calls[call_id]
        call.status = CallStatus.COMPLETED
        call.ended_at = datetime.now()

        # Remove from queue if present
        if call_id in state.queue:
            state.queue.remove(call_id)

        logger.info(f"Call {call_id} completed")

        # Broadcast update
        await broadcast_update("call:ended", {
            "call_id": call_id,
            "duration": call.total_duration_seconds
        })

        return {
            "success": True,
            "call": call.model_dump(),
            "transcript": state.transcripts.get(call_id).model_dump() if call_id in state.transcripts else None,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error ending call {call_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/calls/queue")
async def get_queue():
    """
    Get calls currently in queue

    Returns: List of Call objects in queue
    """
    try:
        queued_calls = [state.active_calls[cid] for cid in state.queue
                       if cid in state.active_calls]

        return {
            "success": True,
            "count": len(queued_calls),
            "calls": [c.model_dump() for c in queued_calls],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching queue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TICKET ENDPOINTS (CRM)
# ============================================================================

@app.post("/api/tickets")
async def create_ticket(
    customer_name: str = Query(...),
    customer_phone: str = Query(...),
    subject: str = Query(...),
    description: str = Query(...),
    call_id: Optional[str] = Query(None),
    priority: str = Query("medium"),
    department: str = Query("complaints")
):
    """
    Create a new support ticket

    Query Parameters:
    - customer_name: Customer name (required)
    - customer_phone: Customer phone (required)
    - subject: Ticket subject (required)
    - description: Ticket description (required)
    - call_id: Associated call ID (optional)
    - priority: Priority level (low, medium, high, urgent)
    - department: Department (reception, sales, complaints)

    Returns: Created Ticket object
    """
    try:
        ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d')}-{uuid4().hex[:4].upper()}"

        ticket = Ticket(
            ticket_id=ticket_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            subject=subject,
            description=description,
            call_id=call_id,
            department=Department(department),
            priority=TicketPriority(priority),
            status=TicketStatus.OPEN
        )

        state.tickets[ticket_id] = ticket

        logger.info(f"Ticket created: {ticket_id}")

        # Broadcast update
        await broadcast_update("ticket:created", ticket.model_dump())

        return {
            "success": True,
            "ticket_id": ticket_id,
            "ticket": ticket.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating ticket: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tickets")
async def get_tickets(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    department: Optional[str] = Query(None)
):
    """
    Get all tickets with optional filters

    Query Parameters:
    - status: Filter by status (optional)
    - priority: Filter by priority (optional)
    - department: Filter by department (optional)

    Returns: List of Ticket objects and stats
    """
    try:
        tickets = list(state.tickets.values())

        if status:
            tickets = [t for t in tickets if t.status.value == status]
        if priority:
            tickets = [t for t in tickets if t.priority.value == priority]
        if department:
            tickets = [t for t in tickets if t.department.value == department]

        # Calculate stats
        stats = {
            "total_customers": len(set(t.customer_phone for t in tickets)),
            "open_tickets": len([t for t in tickets if t.status in [TicketStatus.OPEN, TicketStatus.IN_PROGRESS]]),
            "resolved_tickets": len([t for t in tickets if t.status == TicketStatus.RESOLVED]),
            "avg_resolution_time": 240  # Mock value
        }

        return {
            "success": True,
            "count": len(tickets),
            "tickets": [t.model_dump() for t in tickets],
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching tickets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tickets/{ticket_id}")
async def get_ticket(ticket_id: str = Path(...)):
    """
    Get specific ticket details

    Path Parameters:
    - ticket_id: Ticket ID to retrieve

    Returns: Ticket object
    """
    if ticket_id not in state.tickets:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")

    try:
        ticket = state.tickets[ticket_id]
        return {
            "success": True,
            "ticket": ticket.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching ticket {ticket_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/tickets/{ticket_id}")
async def update_ticket(
    ticket_id: str = Path(...),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    notes: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None)
):
    """
    Update ticket

    Path Parameters:
    - ticket_id: Ticket ID to update

    Query Parameters:
    - status: New status (optional)
    - priority: New priority (optional)
    - notes: Additional notes (optional)
    - assigned_to: Agent ID to assign to (optional)

    Returns: Updated Ticket object
    """
    if ticket_id not in state.tickets:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")

    try:
        ticket = state.tickets[ticket_id]

        if status:
            ticket.status = TicketStatus(status)
            if status == "resolved":
                ticket.resolved_at = datetime.now()

        if priority:
            ticket.priority = TicketPriority(priority)

        if notes:
            ticket.notes = notes

        if assigned_to:
            ticket.assigned_to = assigned_to
            ticket.assigned_at = datetime.now()

        ticket.updated_at = datetime.now()

        logger.info(f"Ticket {ticket_id} updated")

        # Broadcast update
        await broadcast_update("ticket:updated", ticket.model_dump())

        return {
            "success": True,
            "ticket": ticket.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid value: {str(e)}")
    except Exception as e:
        logger.error(f"Error updating ticket {ticket_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CUSTOMER ENDPOINTS
# ============================================================================

@app.get("/api/customers")
async def get_customers():
    """
    Get all customers

    Returns: List of CustomerProfile objects
    """
    try:
        customers = list(state.customers.values())

        return {
            "success": True,
            "count": len(customers),
            "customers": [c.model_dump() for c in customers],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching customers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/{customer_id}")
async def get_customer(customer_id: str = Path(...)):
    """
    Get specific customer details

    Path Parameters:
    - customer_id: Customer ID to retrieve

    Returns: CustomerProfile object
    """
    if customer_id not in state.customers:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    try:
        customer = state.customers[customer_id]
        return {
            "success": True,
            "customer": customer.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching customer {customer_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# AGENT ENDPOINTS
# ============================================================================

@app.get("/api/agents")
async def get_agents(status: Optional[str] = Query(None)):
    """
    Get all agents

    Query Parameters:
    - status: Filter by status (available, busy, on_break, offline)

    Returns: List of Agent objects
    """
    try:
        agents = list(state.agents.values())

        if status:
            agents = [a for a in agents if a.status.value == status]

        return {
            "success": True,
            "count": len(agents),
            "agents": [a.model_dump() for a in agents],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str = Path(...)):
    """
    Get specific agent details

    Path Parameters:
    - agent_id: Agent ID to retrieve

    Returns: Agent object
    """
    if agent_id not in state.agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    try:
        agent = state.agents[agent_id]
        return {
            "success": True,
            "agent": agent.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/agents/{agent_id}/status")
async def update_agent_status(
    agent_id: str = Path(...),
    status: str = Query(...)
):
    """
    Update agent status

    Path Parameters:
    - agent_id: Agent ID to update

    Query Parameters:
    - status: New status (available, busy, on_break, offline)

    Returns: Updated Agent object
    """
    if agent_id not in state.agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    try:
        agent = state.agents[agent_id]
        agent.status = AgentStatus(status)
        agent.last_active = datetime.now()

        logger.info(f"Agent {agent_id} status updated to {status}")

        # Broadcast update
        await broadcast_update("agent:status_changed", {
            "agent_id": agent_id,
            "status": status
        })

        return {
            "success": True,
            "agent": agent.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid status: {str(e)}")
    except Exception as e:
        logger.error(f"Error updating agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TRANSCRIPT ENDPOINTS
# ============================================================================

@app.get("/api/transcripts/{call_id}")
async def get_transcript(call_id: str = Path(...)):
    """
    Get call transcript

    Path Parameters:
    - call_id: Call ID to get transcript for

    Returns: CallTranscript object
    """
    if call_id not in state.transcripts:
        raise HTTPException(status_code=404, detail=f"Transcript for call {call_id} not found")

    try:
        transcript = state.transcripts[call_id]
        return {
            "success": True,
            "transcript": transcript.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching transcript {call_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transcripts/{call_id}/messages")
async def add_transcript_message(
    call_id: str = Path(...),
    speaker: str = Query(...),
    content: str = Query(...),
    language: Optional[str] = Query(None)
):
    """
    Add message to call transcript

    Path Parameters:
    - call_id: Call ID

    Query Parameters:
    - speaker: Speaker type (customer, agent, bot, system)
    - content: Message content
    - language: Language code (ar, en)

    Returns: Updated CallTranscript
    """
    if call_id not in state.transcripts:
        raise HTTPException(status_code=404, detail=f"Transcript for call {call_id} not found")

    try:
        message = TranscriptMessage(
            speaker=speaker,
            content=content,
            language=language,
            timestamp=datetime.now()
        )

        state.transcripts[call_id].messages.append(message)

        logger.info(f"Message added to transcript {call_id}")

        # Broadcast update
        await broadcast_update("message:new", {
            "call_id": call_id,
            "speaker": speaker,
            "content": content
        })

        return {
            "success": True,
            "transcript": state.transcripts[call_id].model_dump(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error adding message to transcript {call_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# WEBSOCKET ENDPOINTS (REAL-TIME UPDATES)
# ============================================================================

async def broadcast_update(event_type: str, data: dict):
    """Broadcast update to all connected WebSocket clients"""
    message = {
        "type": event_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }

    disconnected_clients = []

    for client_id, websocket in state.websocket_connections.items():
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Error sending to WebSocket {client_id}: {str(e)}")
            disconnected_clients.append(client_id)

    # Clean up disconnected clients
    for client_id in disconnected_clients:
        del state.websocket_connections[client_id]

@app.websocket("/ws/updates")
async def websocket_updates(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates

    Sends:
    - call:new - New call added
    - call:updated - Call status/details updated
    - call:routed - Call routed to department
    - call:transferred - Call transferred
    - call:ended - Call ended
    - ticket:created - New ticket created
    - ticket:updated - Ticket updated
    - message:new - New chat message
    - agent:status_changed - Agent status changed
    """
    client_id = f"ws-{uuid4().hex[:8]}"
    await websocket.accept()
    state.websocket_connections[client_id] = websocket

    logger.info(f"WebSocket client connected: {client_id}")

    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connection:established",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat()
        })

        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                logger.debug(f"WebSocket message from {client_id}: {message}")

                # Handle ping/pong
                if message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })

            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from WebSocket {client_id}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {client_id}")
        if client_id in state.websocket_connections:
            del state.websocket_connections[client_id]
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {str(e)}")
        if client_id in state.websocket_connections:
            del state.websocket_connections[client_id]

# ============================================================================
# AGENT DISPATCH ENDPOINTS
# ============================================================================

class AgentDispatchRequest(BaseModel):
    """Request model for dispatching an agent"""
    room_name: str
    user_name: str = "Customer"
    language: str = "ar"


@app.post("/api/dispatch-agent")
async def dispatch_agent(request: AgentDispatchRequest):
    """
    Dispatch a LiveKit agent to join a call room

    This endpoint triggers a call center agent to automatically join a LiveKit
    room and start handling the call with STT/LLM/TTS pipeline.

    Args:
        request: Agent dispatch request with room name, user name, and language

    Returns:
        Status of the dispatch request
    """
    try:
        logger.info(f"🤖 Dispatching agent to room: {request.room_name}")

        # Create or get a job for the agent
        agent_job = {
            "type": "call-center",
            "room_name": request.room_name,
            "user_name": request.user_name,
            "language": request.language,
            "timestamp": datetime.now().isoformat(),
            "job_id": f"job-{uuid4().hex[:8]}"
        }

        # Store the job (in production, this would be in a proper queue system)
        # For now, we'll just log it and return success
        logger.info(f"✅ Agent job created: {agent_job['job_id']}")

        return {
            "success": True,
            "message": "Agent dispatch initiated",
            "job_id": agent_job["job_id"],
            "room_name": request.room_name,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error dispatching agent: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Agent dispatch failed: {str(e)}"
        )

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
