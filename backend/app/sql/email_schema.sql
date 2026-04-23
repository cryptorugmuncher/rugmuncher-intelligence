-- RMI Email Management Schema
-- Run in Supabase SQL Editor

-- ═══════════════════════════════════════════════════════════
-- EMAIL TEMPLATES
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS email_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    subject TEXT NOT NULL,
    html_body TEXT,
    text_body TEXT,
    description TEXT,
    updated_by TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE email_templates ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS "Templates admin write" ON email_templates FOR ALL USING (
    EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.role = 'admin')
);
CREATE POLICY IF NOT EXISTS "Templates public read" ON email_templates FOR SELECT USING (true);

-- ═══════════════════════════════════════════════════════════
-- EMAIL LOGS
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS email_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    to_address TEXT NOT NULL,
    from_address TEXT,
    template_name TEXT,
    subject TEXT,
    status TEXT DEFAULT 'pending',
    error_msg TEXT,
    metadata JSONB DEFAULT '{}',
    sent_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE email_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS "Logs admin read" ON email_logs FOR SELECT USING (
    EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.role = 'admin')
);
CREATE POLICY IF NOT EXISTS "Logs system insert" ON email_logs FOR INSERT WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_email_logs_sent_at ON email_logs(sent_at DESC);
CREATE INDEX IF NOT EXISTS idx_email_logs_status ON email_logs(status);
CREATE INDEX IF NOT EXISTS idx_email_logs_to ON email_logs(to_address);

-- ═══════════════════════════════════════════════════════════
-- CONTACT SUBMISSIONS
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS contact_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    status TEXT DEFAULT 'new',
    reply_message TEXT,
    replied_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE contact_submissions ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS "Contact public insert" ON contact_submissions FOR INSERT WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Contact admin all" ON contact_submissions FOR ALL USING (
    EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.role = 'admin')
);

CREATE INDEX IF NOT EXISTS idx_contact_status ON contact_submissions(status);
CREATE INDEX IF NOT EXISTS idx_contact_created ON contact_submissions(created_at DESC);

-- ═══════════════════════════════════════════════════════════
-- EMAIL FORWARDING RULES
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS email_forwarding_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alias_address TEXT UNIQUE NOT NULL,
    forward_to TEXT NOT NULL,
    description TEXT,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE email_forwarding_rules ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS "Forwarding admin all" ON email_forwarding_rules FOR ALL USING (
    EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.role = 'admin')
);
CREATE POLICY IF NOT EXISTS "Forwarding public read" ON email_forwarding_rules FOR SELECT USING (true);

-- Seed default business emails
INSERT INTO email_forwarding_rules (alias_address, forward_to, description)
VALUES
    ('admin@cryptorugmunch.com', 'cryptorugmuncher@gmail.com', 'Platform administration'),
    ('biz@rugmunch.io', 'cryptorugmuncher@gmail.com', 'Business inquiries'),
    ('work@cryptorugmunch.com', 'cryptorugmuncher@gmail.com', 'Internal team communications'),
    ('support@cryptorugmunch.com', 'cryptorugmuncher@gmail.com', 'User support'),
    ('hello@rugmunch.io', 'cryptorugmuncher@gmail.com', 'General inquiries'),
    ('legal@cryptorugmunch.com', 'cryptorugmuncher@gmail.com', 'Legal notices'),
    ('partnerships@rugmunch.io', 'cryptorugmuncher@gmail.com', 'Partnerships'),
    ('press@cryptorugmunch.com', 'cryptorugmuncher@gmail.com', 'Press inquiries'),
    ('security@cryptorugmunch.com', 'cryptorugmuncher@gmail.com', 'Security reports'),
    ('notifications@rugmunch.io', 'cryptorugmuncher@gmail.com', 'Automated notifications')
ON CONFLICT (alias_address) DO NOTHING;
