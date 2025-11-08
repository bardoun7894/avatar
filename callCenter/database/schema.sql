-- Call Center Database Schema
-- PostgreSQL tables for call center system
-- These tables extend the existing avatary schema

-- ============================================================================
-- CALLS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS calls (
    call_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(20),
    direction VARCHAR(20) NOT NULL DEFAULT 'inbound',
    customer_name VARCHAR(255),
    customer_email VARCHAR(255),
    customer_phone VARCHAR(20),

    -- Call status and routing
    status VARCHAR(50) NOT NULL DEFAULT 'initiated',
    department VARCHAR(50),
    service_type VARCHAR(255),
    assigned_agent_id UUID REFERENCES agents(agent_id) ON DELETE SET NULL,

    -- IVR state
    ivr_stage VARCHAR(50) DEFAULT 'welcome',

    -- Timing
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMP,
    queue_time_seconds INTEGER DEFAULT 0,
    talk_time_seconds INTEGER DEFAULT 0,
    total_duration_seconds INTEGER DEFAULT 0,

    -- Data collection
    collected_data JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',

    -- Flags
    bot_response_count INTEGER DEFAULT 0,
    transferred_to_agent BOOLEAN DEFAULT FALSE,

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for calls
CREATE INDEX idx_calls_status ON calls(status);
CREATE INDEX idx_calls_department ON calls(department);
CREATE INDEX idx_calls_started_at ON calls(started_at);
CREATE INDEX idx_calls_customer_phone ON calls(customer_phone);
CREATE INDEX idx_calls_assigned_agent ON calls(assigned_agent_id);


-- ============================================================================
-- CUSTOMERS TABLE (CRM)
-- ============================================================================
CREATE TABLE IF NOT EXISTS customers (
    customer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,

    -- Interaction history
    total_calls INTEGER DEFAULT 0,
    total_tickets INTEGER DEFAULT 0,
    last_interaction TIMESTAMP,

    -- Contact details
    company_name VARCHAR(255),
    address TEXT,

    -- Notes and tags
    notes TEXT,
    tags TEXT[] DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for customers
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_created_at ON customers(created_at);


-- ============================================================================
-- TICKETS TABLE (CRM)
-- ============================================================================
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id UUID REFERENCES calls(call_id) ON DELETE SET NULL,
    customer_id UUID REFERENCES customers(customer_id) ON DELETE CASCADE,

    customer_name VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    customer_email VARCHAR(255),

    -- Ticket details
    subject VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    department VARCHAR(50) DEFAULT 'complaints',
    status VARCHAR(50) NOT NULL DEFAULT 'open',
    priority VARCHAR(50) NOT NULL DEFAULT 'medium',

    -- Assignment
    assigned_to UUID REFERENCES agents(agent_id) ON DELETE SET NULL,
    assigned_at TIMESTAMP,

    -- Resolution tracking
    notes TEXT,
    resolution_notes TEXT,
    tags TEXT[] DEFAULT '{}',
    custom_fields JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMP
);

-- Indexes for tickets
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_priority ON tickets(priority);
CREATE INDEX idx_tickets_department ON tickets(department);
CREATE INDEX idx_tickets_customer_id ON tickets(customer_id);
CREATE INDEX idx_tickets_assigned_to ON tickets(assigned_to);
CREATE INDEX idx_tickets_created_at ON tickets(created_at);


-- ============================================================================
-- TICKETS HISTORY TABLE (Audit trail)
-- ============================================================================
CREATE TABLE IF NOT EXISTS tickets_history (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID NOT NULL REFERENCES tickets(ticket_id) ON DELETE CASCADE,

    -- Status change tracking
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    old_priority VARCHAR(50),
    new_priority VARCHAR(50),

    -- Who made the change
    changed_by UUID REFERENCES agents(agent_id) ON DELETE SET NULL,
    change_reason TEXT,

    -- Timestamp
    changed_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for tickets_history
CREATE INDEX idx_tickets_history_ticket_id ON tickets_history(ticket_id);
CREATE INDEX idx_tickets_history_changed_at ON tickets_history(changed_at);


-- ============================================================================
-- AGENTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS agents (
    agent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    department VARCHAR(50) NOT NULL DEFAULT 'reception',
    status VARCHAR(50) NOT NULL DEFAULT 'offline',

    -- Skills and limits
    skills TEXT[] DEFAULT '{}',
    max_concurrent_calls INTEGER DEFAULT 1 CHECK (max_concurrent_calls > 0),
    current_call_count INTEGER DEFAULT 0,

    -- Performance stats
    total_calls_handled INTEGER DEFAULT 0,
    avg_handling_time_seconds INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_active TIMESTAMP
);

-- Indexes for agents
CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_agents_department ON agents(department);


-- ============================================================================
-- CALL TRANSCRIPTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS call_transcripts (
    transcript_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id UUID UNIQUE NOT NULL REFERENCES calls(call_id) ON DELETE CASCADE,

    customer_name VARCHAR(255),
    agent_name VARCHAR(255),
    department VARCHAR(50),

    -- Transcript content
    transcript_text TEXT,
    messages JSONB,  -- Array of {timestamp, speaker, content, language}

    -- Analysis
    sentiment VARCHAR(50),  -- positive, neutral, negative
    summary TEXT,
    keywords TEXT[] DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for transcripts
CREATE INDEX idx_transcripts_call_id ON call_transcripts(call_id);
CREATE INDEX idx_transcripts_created_at ON call_transcripts(created_at);


-- ============================================================================
-- QUEUE MANAGEMENT TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS call_queue (
    queue_entry_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id UUID NOT NULL REFERENCES calls(call_id) ON DELETE CASCADE,

    department VARCHAR(50) NOT NULL,
    position_in_queue INTEGER NOT NULL,

    -- Timing
    entered_queue_at TIMESTAMP NOT NULL DEFAULT NOW(),
    exited_queue_at TIMESTAMP,
    wait_time_seconds INTEGER,

    -- Status
    status VARCHAR(50) DEFAULT 'waiting'
);

-- Indexes for queue
CREATE INDEX idx_queue_department ON call_queue(department);
CREATE INDEX idx_queue_status ON call_queue(status);
CREATE INDEX idx_queue_call_id ON call_queue(call_id);


-- ============================================================================
-- ANALYTICS TABLES
-- ============================================================================

-- Daily department statistics
CREATE TABLE IF NOT EXISTS department_daily_stats (
    stat_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stat_date DATE NOT NULL,
    department VARCHAR(50) NOT NULL,

    -- Call metrics
    total_calls INTEGER DEFAULT 0,
    completed_calls INTEGER DEFAULT 0,
    abandoned_calls INTEGER DEFAULT 0,
    avg_wait_time_seconds INTEGER DEFAULT 0,
    avg_handling_time_seconds INTEGER DEFAULT 0,

    -- Quality metrics
    calls_transferred INTEGER DEFAULT 0,
    customer_satisfaction_rate FLOAT DEFAULT 0.0,

    -- Peak hour
    peak_hour VARCHAR(5),

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(stat_date, department)
);

-- Agent performance metrics
CREATE TABLE IF NOT EXISTS agent_performance (
    performance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    agent_name VARCHAR(255),

    metric_date DATE NOT NULL,

    -- Performance metrics
    calls_handled INTEGER DEFAULT 0,
    avg_call_duration_seconds INTEGER DEFAULT 0,
    customer_satisfaction_rate FLOAT DEFAULT 0.0,
    tickets_created INTEGER DEFAULT 0,
    tickets_resolved INTEGER DEFAULT 0,
    escalation_rate FLOAT DEFAULT 0.0,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(agent_id, metric_date)
);

-- Indexes for analytics
CREATE INDEX idx_dept_stats_date ON department_daily_stats(stat_date);
CREATE INDEX idx_agent_perf_date ON agent_performance(metric_date);
CREATE INDEX idx_agent_perf_agent_id ON agent_performance(agent_id_id);


-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Active calls view
CREATE OR REPLACE VIEW active_calls AS
SELECT c.*, a.name as agent_name
FROM calls c
LEFT JOIN agents a ON c.assigned_agent_id = a.agent_id
WHERE c.status IN ('initiated', 'ivr_processing', 'in_queue', 'in_progress', 'transferred');

-- Open tickets view
CREATE OR REPLACE VIEW open_tickets AS
SELECT t.*, a.name as agent_name
FROM tickets t
LEFT JOIN agents a ON t.assigned_to = a.agent_id
WHERE t.status IN ('open', 'in_progress', 'pending');

-- Agent availability view
CREATE OR REPLACE VIEW agent_availability AS
SELECT
    agent_id,
    name,
    department,
    status,
    max_concurrent_calls,
    current_call_count,
    (max_concurrent_calls - current_call_count) as available_slots,
    CASE WHEN status = 'available' AND current_call_count < max_concurrent_calls
         THEN true ELSE false END as is_available
FROM agents;


-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to update call duration
CREATE OR REPLACE FUNCTION update_call_duration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.ended_at IS NOT NULL AND NEW.started_at IS NOT NULL THEN
        NEW.total_duration_seconds := EXTRACT(EPOCH FROM (NEW.ended_at - NEW.started_at))::INTEGER;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for call duration
CREATE TRIGGER trigger_update_call_duration
BEFORE UPDATE ON calls
FOR EACH ROW
EXECUTE FUNCTION update_call_duration();


-- Function to increment customer call count
CREATE OR REPLACE FUNCTION increment_customer_calls()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.customer_id IS NOT NULL THEN
        UPDATE customers
        SET total_calls = total_calls + 1,
            last_interaction = NOW()
        WHERE customer_id = NEW.customer_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for customer call count
CREATE TRIGGER trigger_increment_customer_calls
AFTER INSERT ON calls
FOR EACH ROW
EXECUTE FUNCTION increment_customer_calls();


-- ============================================================================
-- PERMISSIONS
-- ============================================================================
-- Assuming you have an app user for the backend
-- GRANT SELECT, INSERT, UPDATE ON calls TO app_user;
-- GRANT SELECT, INSERT, UPDATE ON customers TO app_user;
-- GRANT SELECT, INSERT, UPDATE ON tickets TO app_user;
-- GRANT SELECT, INSERT ON call_transcripts TO app_user;
