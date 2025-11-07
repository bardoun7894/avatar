-- Create appointments table in Supabase
-- Run this in your Supabase SQL Editor

CREATE TABLE IF NOT EXISTS appointments (
    id TEXT PRIMARY KEY,
    patient_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    service TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    notes TEXT,
    status TEXT DEFAULT 'confirmed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_appointments_phone ON appointments(phone);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(date);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);

-- Enable Row Level Security (RLS)
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (adjust as needed for production)
CREATE POLICY "Enable all access for appointments" ON appointments
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Insert sample data (optional)
INSERT INTO appointments (id, patient_name, phone, email, service, date, time, notes, status, created_at)
VALUES
    ('APT0001', 'أحمد محمد', '+966501234567', 'ahmad@example.com', 'تنظيف', '2025-11-10', '10:00', 'أول زيارة', 'confirmed', NOW()),
    ('APT0002', 'محمد البردوني', '0715815341', 'محمد@atjmail.com', 'تنظيف الأسنان', '2023-11-26', '11:00', '', 'confirmed', NOW())
ON CONFLICT (id) DO NOTHING;

-- Grant permissions
GRANT ALL ON appointments TO anon;
GRANT ALL ON appointments TO authenticated;
