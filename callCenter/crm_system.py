#!/usr/bin/env python3
"""
CRM System for Call Center
Manages customers, tickets, and basic customer relationship features
"""

import logging
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime

# Use absolute imports - Docker runs with all files in /app
from models import (
    Ticket,
    TicketStatus,
    TicketPriority,
    Department,
    CustomerProfile,
    Call,
)
from rules_engine import get_rules_engine
from config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

# Import Supabase client (reuse from avatary)
try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("Supabase client not available. Using mock storage.")


# ============================================================================
# CRM SYSTEM CLASS
# ============================================================================

class CRMSystem:
    """
    Basic CRM system for managing customers and tickets
    Features:
    - Customer profile management
    - Ticket creation and tracking
    - Ticket status updates
    - Basic ticket assignment
    """

    def __init__(self):
        self.rules_engine = get_rules_engine()
        self.supabase = None

        if SUPABASE_AVAILABLE and SUPABASE_URL and SUPABASE_KEY:
            try:
                self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                logger.info("CRM System initialized with Supabase")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase: {e}")
                self.supabase = None
        else:
            logger.warning("CRM System using mock storage (no database available)")

        # Mock storage for development
        self.mock_customers: Dict[str, CustomerProfile] = {}
        self.mock_tickets: Dict[str, Ticket] = {}

    # ========================================================================
    # CUSTOMER MANAGEMENT
    # ========================================================================

    async def create_or_update_customer(
        self, phone: str, name: str, email: Optional[str] = None
    ) -> CustomerProfile:
        """
        Create new customer or update existing
        """
        try:
            # Check if customer exists by phone
            customer = await self.get_customer_by_phone(phone)

            if customer:
                # Update existing
                customer.name = name
                if email:
                    customer.email = email
                customer.updated_at = datetime.now()
                customer.last_interaction = datetime.now()

                if self.supabase:
                    await self._update_customer_in_db(customer)
                else:
                    self.mock_customers[customer.customer_id] = customer

                logger.info(f"Updated customer: {phone}")
                return customer

            # Create new customer
            new_customer = CustomerProfile(
                customer_id=str(uuid.uuid4()),
                name=name,
                phone=phone,
                email=email,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            if self.supabase:
                await self._insert_customer_in_db(new_customer)
            else:
                self.mock_customers[new_customer.customer_id] = new_customer

            logger.info(f"Created new customer: {phone}")
            return new_customer

        except Exception as e:
            logger.error(f"Error creating/updating customer: {e}")
            raise

    async def get_customer_by_phone(self, phone: str) -> Optional[CustomerProfile]:
        """
        Retrieve customer by phone number
        """
        try:
            # Try database first
            if self.supabase:
                response = await self._query_customer_from_db(phone)
                if response:
                    return response

            # Check mock storage
            for customer in self.mock_customers.values():
                if customer.phone == phone:
                    return customer

            return None

        except Exception as e:
            logger.error(f"Error retrieving customer: {e}")
            return None

    async def get_customer_by_id(self, customer_id: str) -> Optional[CustomerProfile]:
        """
        Retrieve customer by ID
        """
        try:
            if self.supabase:
                response = await self._query_customer_by_id_from_db(customer_id)
                if response:
                    return response

            return self.mock_customers.get(customer_id)

        except Exception as e:
            logger.error(f"Error retrieving customer: {e}")
            return None

    # ========================================================================
    # TICKET MANAGEMENT
    # ========================================================================

    async def create_ticket(
        self,
        customer_name: str,
        customer_phone: str,
        subject: str,
        description: str,
        department: Department = Department.COMPLAINTS,
        priority: TicketPriority = TicketPriority.MEDIUM,
        call_id: Optional[str] = None,
        customer_email: Optional[str] = None,
    ) -> Ticket:
        """
        Create a new ticket
        Typically called automatically from complaints department
        """
        try:
            # Get or create customer
            customer = await self.create_or_update_customer(
                phone=customer_phone, name=customer_name, email=customer_email
            )

            # Create ticket
            ticket = Ticket(
                ticket_id=f"TKT{str(uuid.uuid4())[:8].upper()}",
                customer_name=customer_name,
                customer_phone=customer_phone,
                customer_email=customer_email,
                subject=subject,
                description=description,
                call_id=call_id,
                department=department,
                priority=priority,
                status=TicketStatus.OPEN,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            # Save to database
            if self.supabase:
                await self._insert_ticket_in_db(ticket)
            else:
                self.mock_tickets[ticket.ticket_id] = ticket

            # Update customer ticket count
            if customer:
                customer.total_tickets += 1
                if self.supabase:
                    await self._update_customer_in_db(customer)
                else:
                    self.mock_customers[customer.customer_id] = customer

            logger.info(f"Created ticket {ticket.ticket_id} for {customer_name}")
            return ticket

        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            raise

    async def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """
        Retrieve ticket by ID
        """
        try:
            if self.supabase:
                response = await self._query_ticket_from_db(ticket_id)
                if response:
                    return response

            return self.mock_tickets.get(ticket_id)

        except Exception as e:
            logger.error(f"Error retrieving ticket: {e}")
            return None

    async def get_customer_tickets(self, customer_phone: str) -> List[Ticket]:
        """
        Get all tickets for a customer
        """
        try:
            # Get customer first
            customer = await self.get_customer_by_phone(customer_phone)
            if not customer:
                return []

            # Get tickets from database
            if self.supabase:
                response = await self._query_tickets_by_customer_from_db(customer_phone)
                return response or []

            # Get from mock storage
            return [t for t in self.mock_tickets.values() if t.customer_phone == customer_phone]

        except Exception as e:
            logger.error(f"Error retrieving customer tickets: {e}")
            return []

    async def update_ticket_status(
        self,
        ticket_id: str,
        new_status: TicketStatus,
        changed_by: Optional[str] = None,
        change_reason: Optional[str] = None,
    ) -> Optional[Ticket]:
        """
        Update ticket status
        """
        try:
            ticket = await self.get_ticket(ticket_id)
            if not ticket:
                return None

            old_status = ticket.status

            # Update status
            ticket.status = new_status
            ticket.updated_at = datetime.now()

            if new_status == TicketStatus.RESOLVED:
                ticket.resolved_at = datetime.now()

            # Save to database
            if self.supabase:
                await self._update_ticket_in_db(ticket)
                # Log to history
                if changed_by:
                    await self._log_ticket_change(
                        ticket_id, old_status, new_status, changed_by, change_reason
                    )
            else:
                self.mock_tickets[ticket_id] = ticket

            logger.info(f"Updated ticket {ticket_id} status to {new_status}")
            return ticket

        except Exception as e:
            logger.error(f"Error updating ticket status: {e}")
            return None

    async def assign_ticket(
        self, ticket_id: str, agent_id: str
    ) -> Optional[Ticket]:
        """
        Assign ticket to an agent
        """
        try:
            ticket = await self.get_ticket(ticket_id)
            if not ticket:
                return None

            ticket.assigned_to = agent_id
            ticket.assigned_at = datetime.now()
            ticket.updated_at = datetime.now()
            ticket.status = TicketStatus.IN_PROGRESS

            # Save to database
            if self.supabase:
                await self._update_ticket_in_db(ticket)
            else:
                self.mock_tickets[ticket_id] = ticket

            logger.info(f"Assigned ticket {ticket_id} to agent {agent_id}")
            return ticket

        except Exception as e:
            logger.error(f"Error assigning ticket: {e}")
            return None

    # ========================================================================
    # AUTO-TICKET CREATION FROM CALLS
    # ========================================================================

    async def auto_create_ticket_from_call(self, call: Call) -> Optional[Ticket]:
        """
        Automatically create ticket from complaint call
        Called by call center agent when call is complaints department
        """
        try:
            # Check if auto ticket creation is enabled
            if not self.rules_engine.should_auto_create_ticket():
                return None

            # Determine priority
            complaint_description = call.collected_data.get(
                "complaint_description", ""
            )
            priority = self.rules_engine.determine_ticket_priority(
                complaint_description
            )

            # Create ticket
            ticket = await self.create_ticket(
                customer_name=call.customer_name or "Unknown",
                customer_phone=call.customer_phone or "",
                subject=call.collected_data.get("complaint_type", "General Complaint"),
                description=complaint_description,
                department=Department.COMPLAINTS,
                priority=priority,
                call_id=call.call_id,
                customer_email=call.customer_email,
            )

            logger.info(f"Auto-created ticket {ticket.ticket_id} from call {call.call_id}")
            return ticket

        except Exception as e:
            logger.error(f"Error auto-creating ticket from call: {e}")
            return None

    # ========================================================================
    # OPEN TICKETS DASHBOARD DATA
    # ========================================================================

    async def get_open_tickets(
        self, department: Optional[Department] = None
    ) -> List[Ticket]:
        """
        Get all open tickets, optionally filtered by department
        """
        try:
            open_statuses = [TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.PENDING]

            if self.supabase:
                tickets = await self._query_open_tickets_from_db(department)
                return tickets or []

            # Get from mock storage
            tickets = [
                t for t in self.mock_tickets.values()
                if t.status in open_statuses and (not department or t.department == department)
            ]
            return tickets

        except Exception as e:
            logger.error(f"Error retrieving open tickets: {e}")
            return []

    async def get_unassigned_tickets(
        self, department: Optional[Department] = None
    ) -> List[Ticket]:
        """
        Get unassigned tickets (for agent dashboard)
        """
        try:
            if self.supabase:
                tickets = await self._query_unassigned_tickets_from_db(department)
                return tickets or []

            tickets = [
                t for t in self.mock_tickets.values()
                if not t.assigned_to and (not department or t.department == department)
            ]
            return tickets

        except Exception as e:
            logger.error(f"Error retrieving unassigned tickets: {e}")
            return []

    # ========================================================================
    # DATABASE OPERATIONS (Mock for now)
    # ========================================================================

    async def _insert_customer_in_db(self, customer: CustomerProfile) -> bool:
        """Insert customer into Supabase database"""
        if not self.supabase:
            return False

        try:
            data = {
                "customer_id": customer.customer_id,
                "name": customer.name,
                "phone": customer.phone,
                "email": customer.email,
                "tier": customer.tier,
                "vip": customer.vip,
                "created_at": customer.created_at.isoformat() if customer.created_at else None,
                "updated_at": customer.updated_at.isoformat() if customer.updated_at else None,
                "last_interaction": customer.last_interaction.isoformat() if customer.last_interaction else None,
                "total_calls": customer.total_calls,
                "total_tickets": customer.total_tickets
            }

            response = self.supabase.table("customers").insert(data).execute()
            logger.info(f"✅ Customer inserted: {customer.phone}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to insert customer to Supabase: {e}")
            return False

    async def _update_customer_in_db(self, customer: CustomerProfile) -> bool:
        """Update customer in Supabase database"""
        if not self.supabase:
            return False

        try:
            data = {
                "name": customer.name,
                "phone": customer.phone,
                "email": customer.email,
                "tier": customer.tier,
                "vip": customer.vip,
                "updated_at": customer.updated_at.isoformat() if customer.updated_at else None,
                "last_interaction": customer.last_interaction.isoformat() if customer.last_interaction else None,
                "total_calls": customer.total_calls,
                "total_tickets": customer.total_tickets
            }

            response = self.supabase.table("customers").update(data).eq(
                "customer_id", customer.customer_id
            ).execute()

            logger.info(f"✅ Customer updated: {customer.phone}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update customer in Supabase: {e}")
            return False

    async def _query_customer_from_db(self, phone: str) -> Optional[CustomerProfile]:
        """Query customer from Supabase by phone number"""
        if not self.supabase:
            return None

        try:
            response = self.supabase.table("customers").select("*").eq(
                "phone", phone
            ).execute()

            if response.data and len(response.data) > 0:
                row = response.data[0]
                customer = CustomerProfile(
                    customer_id=row["customer_id"],
                    name=row["name"],
                    phone=row["phone"],
                    email=row.get("email"),
                    tier=row.get("tier", "starter"),
                    vip=row.get("vip", False),
                    created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else None,
                    updated_at=datetime.fromisoformat(row["updated_at"]) if row.get("updated_at") else None,
                )
                customer.last_interaction = datetime.fromisoformat(row["last_interaction"]) if row.get("last_interaction") else None
                customer.total_calls = row.get("total_calls", 0)
                customer.total_tickets = row.get("total_tickets", 0)

                logger.info(f"✅ Retrieved customer from DB: {phone}")
                return customer

            return None

        except Exception as e:
            logger.error(f"❌ Failed to query customer from Supabase: {e}")
            return None

    async def _query_customer_by_id_from_db(
        self, customer_id: str
    ) -> Optional[CustomerProfile]:
        """Query customer from Supabase by ID"""
        if not self.supabase:
            return None

        try:
            response = self.supabase.table("customers").select("*").eq(
                "customer_id", customer_id
            ).execute()

            if response.data and len(response.data) > 0:
                row = response.data[0]
                customer = CustomerProfile(
                    customer_id=row["customer_id"],
                    name=row["name"],
                    phone=row["phone"],
                    email=row.get("email"),
                    tier=row.get("tier", "starter"),
                    vip=row.get("vip", False),
                    created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else None,
                    updated_at=datetime.fromisoformat(row["updated_at"]) if row.get("updated_at") else None,
                )
                customer.last_interaction = datetime.fromisoformat(row["last_interaction"]) if row.get("last_interaction") else None
                customer.total_calls = row.get("total_calls", 0)
                customer.total_tickets = row.get("total_tickets", 0)

                logger.info(f"✅ Retrieved customer from DB by ID: {customer_id}")
                return customer

            return None

        except Exception as e:
            logger.error(f"❌ Failed to query customer from Supabase: {e}")
            return None

    async def _insert_ticket_in_db(self, ticket: Ticket) -> bool:
        """Insert ticket into Supabase database"""
        if not self.supabase:
            return False

        try:
            data = {
                "ticket_id": ticket.ticket_id,
                "customer_phone": ticket.customer_phone,
                "customer_name": ticket.customer_name,
                "customer_email": ticket.customer_email,
                "subject": ticket.subject,
                "description": ticket.description,
                "department": ticket.department.value,
                "priority": ticket.priority.value,
                "status": ticket.status.value,
                "call_id": ticket.call_id,
                "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
                "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
            }

            response = self.supabase.table("tickets").insert(data).execute()
            logger.info(f"✅ Ticket inserted: {ticket.ticket_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to insert ticket to Supabase: {e}")
            return False

    async def _update_ticket_in_db(self, ticket: Ticket) -> bool:
        """Update ticket in Supabase database"""
        if not self.supabase:
            return False

        try:
            data = {
                "subject": ticket.subject,
                "description": ticket.description,
                "department": ticket.department.value,
                "priority": ticket.priority.value,
                "status": ticket.status.value,
                "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
            }

            response = self.supabase.table("tickets").update(data).eq(
                "ticket_id", ticket.ticket_id
            ).execute()

            logger.info(f"✅ Ticket updated: {ticket.ticket_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update ticket in Supabase: {e}")
            return False

    async def _query_ticket_from_db(self, ticket_id: str) -> Optional[Ticket]:
        """Query ticket from Supabase by ID"""
        if not self.supabase:
            return None

        try:
            response = self.supabase.table("tickets").select("*").eq(
                "ticket_id", ticket_id
            ).execute()

            if response.data and len(response.data) > 0:
                row = response.data[0]
                ticket = Ticket(
                    ticket_id=row["ticket_id"],
                    customer_phone=row["customer_phone"],
                    customer_name=row["customer_name"],
                    customer_email=row.get("customer_email"),
                    subject=row["subject"],
                    description=row["description"],
                    department=Department(row["department"]),
                    priority=TicketPriority(row["priority"]),
                    status=TicketStatus(row["status"]),
                    call_id=row.get("call_id"),
                    created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else None,
                    updated_at=datetime.fromisoformat(row["updated_at"]) if row.get("updated_at") else None,
                )

                logger.info(f"✅ Retrieved ticket from DB: {ticket_id}")
                return ticket

            return None

        except Exception as e:
            logger.error(f"❌ Failed to query ticket from Supabase: {e}")
            return None

    async def _query_tickets_by_customer_from_db(
        self, customer_phone: str
    ) -> List[Ticket]:
        """Query tickets from Supabase by customer phone"""
        if not self.supabase:
            return []

        try:
            response = self.supabase.table("tickets").select("*").eq(
                "customer_phone", customer_phone
            ).execute()

            tickets = []
            if response.data:
                for row in response.data:
                    ticket = Ticket(
                        ticket_id=row["ticket_id"],
                        customer_phone=row["customer_phone"],
                        customer_name=row["customer_name"],
                        customer_email=row.get("customer_email"),
                        subject=row["subject"],
                        description=row["description"],
                        department=Department(row["department"]),
                        priority=TicketPriority(row["priority"]),
                        status=TicketStatus(row["status"]),
                        call_id=row.get("call_id"),
                        created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else None,
                        updated_at=datetime.fromisoformat(row["updated_at"]) if row.get("updated_at") else None,
                    )
                    tickets.append(ticket)

            logger.info(f"✅ Retrieved {len(tickets)} tickets for {customer_phone}")
            return tickets

        except Exception as e:
            logger.error(f"❌ Failed to query tickets from Supabase: {e}")
            return []

    async def _query_open_tickets_from_db(
        self, department: Optional[Department] = None
    ) -> List[Ticket]:
        """Query open tickets from Supabase"""
        if not self.supabase:
            return []

        try:
            query = self.supabase.table("tickets").select("*").eq("status", TicketStatus.OPEN.value)

            if department:
                query = query.eq("department", department.value)

            response = query.execute()

            tickets = []
            if response.data:
                for row in response.data:
                    ticket = Ticket(
                        ticket_id=row["ticket_id"],
                        customer_phone=row["customer_phone"],
                        customer_name=row["customer_name"],
                        customer_email=row.get("customer_email"),
                        subject=row["subject"],
                        description=row["description"],
                        department=Department(row["department"]),
                        priority=TicketPriority(row["priority"]),
                        status=TicketStatus(row["status"]),
                        call_id=row.get("call_id"),
                        created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else None,
                        updated_at=datetime.fromisoformat(row["updated_at"]) if row.get("updated_at") else None,
                    )
                    tickets.append(ticket)

            logger.info(f"✅ Retrieved {len(tickets)} open tickets")
            return tickets

        except Exception as e:
            logger.error(f"❌ Failed to query open tickets from Supabase: {e}")
            return []

    async def _query_unassigned_tickets_from_db(
        self, department: Optional[Department] = None
    ) -> List[Ticket]:
        """Query unassigned tickets from Supabase"""
        if not self.supabase:
            return []

        try:
            query = self.supabase.table("tickets").select("*").eq(
                "status", TicketStatus.UNASSIGNED.value
            )

            if department:
                query = query.eq("department", department.value)

            response = query.execute()

            tickets = []
            if response.data:
                for row in response.data:
                    ticket = Ticket(
                        ticket_id=row["ticket_id"],
                        customer_phone=row["customer_phone"],
                        customer_name=row["customer_name"],
                        customer_email=row.get("customer_email"),
                        subject=row["subject"],
                        description=row["description"],
                        department=Department(row["department"]),
                        priority=TicketPriority(row["priority"]),
                        status=TicketStatus(row["status"]),
                        call_id=row.get("call_id"),
                        created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else None,
                        updated_at=datetime.fromisoformat(row["updated_at"]) if row.get("updated_at") else None,
                    )
                    tickets.append(ticket)

            logger.info(f"✅ Retrieved {len(tickets)} unassigned tickets")
            return tickets

        except Exception as e:
            logger.error(f"❌ Failed to query unassigned tickets from Supabase: {e}")
            return []

    async def _log_ticket_change(
        self,
        ticket_id: str,
        old_status: TicketStatus,
        new_status: TicketStatus,
        changed_by: str,
        reason: Optional[str] = None,
    ) -> bool:
        """Log ticket status change to Supabase"""
        if not self.supabase:
            return False

        try:
            data = {
                "ticket_id": ticket_id,
                "old_status": old_status.value,
                "new_status": new_status.value,
                "changed_by": changed_by,
                "reason": reason,
                "changed_at": datetime.utcnow().isoformat()
            }

            response = self.supabase.table("ticket_history").insert(data).execute()
            logger.info(f"✅ Logged status change for ticket {ticket_id}: {old_status.value} → {new_status.value}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to log ticket change: {e}")
            return False


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_crm = None


def get_crm_system() -> CRMSystem:
    """Get or create CRM system instance"""
    global _crm
    if _crm is None:
        _crm = CRMSystem()
    return _crm


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "CRMSystem",
    "get_crm_system",
]
