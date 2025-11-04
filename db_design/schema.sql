-- Agile Budget Tracker Database Schema
-- PostgreSQL 15+

-- Enable UUID extension for generating unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table with role-based access
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    role VARCHAR(20) NOT NULL CHECK (role IN ('PM', 'FINANCE', 'DEV', 'ADMIN')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'COMPLETED', 'ON_HOLD', 'CANCELLED')),
    budget DECIMAL(12, 2),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Sprints table
CREATE TABLE sprints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    sprint_number INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'PLANNED' CHECK (status IN ('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')),
    goal TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_project_sprint UNIQUE (project_id, sprint_number),
    CONSTRAINT valid_sprint_dates CHECK (end_date >= start_date)
);

-- Sprint metrics table for financial tracking
CREATE TABLE sprint_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sprint_id UUID NOT NULL REFERENCES sprints(id) ON DELETE CASCADE,
    sprint_cost DECIMAL(12, 2) NOT NULL CHECK (sprint_cost >= 0),
    estimated_business_value DECIMAL(12, 2) NOT NULL CHECK (estimated_business_value >= 0),
    velocity INTEGER NOT NULL CHECK (velocity >= 0),
    actual_business_value DECIMAL(12, 2) CHECK (actual_business_value >= 0),
    roi DECIMAL(10, 4) GENERATED ALWAYS AS (
        CASE 
            WHEN sprint_cost > 0 THEN 
                ((estimated_business_value - sprint_cost) / sprint_cost) * 100
            ELSE NULL
        END
    ) STORED,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_sprint_metrics UNIQUE (sprint_id)
);

-- Create indexes for better query performance
CREATE INDEX idx_projects_owner ON projects(owner_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_sprints_project ON sprints(project_id);
CREATE INDEX idx_sprints_status ON sprints(status);
CREATE INDEX idx_sprints_dates ON sprints(start_date, end_date);
CREATE INDEX idx_sprint_metrics_sprint ON sprint_metrics(sprint_id);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_email ON users(email);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to auto-update updated_at on all tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sprints_updated_at BEFORE UPDATE ON sprints
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sprint_metrics_updated_at BEFORE UPDATE ON sprint_metrics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for development
INSERT INTO users (username, email, first_name, last_name, role) VALUES
    ('admin', 'admin@example.com', 'Admin', 'User', 'ADMIN'),
    ('john_pm', 'john@example.com', 'John', 'Doe', 'PM'),
    ('jane_finance', 'jane@example.com', 'Jane', 'Smith', 'FINANCE'),
    ('bob_dev', 'bob@example.com', 'Bob', 'Johnson', 'DEV');

COMMENT ON TABLE users IS 'Stores user accounts with role-based access control';
COMMENT ON TABLE projects IS 'Stores project information and budget allocations';
COMMENT ON TABLE sprints IS 'Stores sprint information linked to projects';
COMMENT ON TABLE sprint_metrics IS 'Stores financial metrics and ROI calculations for each sprint';
COMMENT ON COLUMN sprint_metrics.roi IS 'Auto-calculated ROI percentage based on business value and cost';