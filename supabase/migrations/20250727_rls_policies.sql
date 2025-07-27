-- Aurum Life MVP v1.2 - Row Level Security Policies
-- Ensures complete data isolation between users
-- Run this migration in Supabase SQL Editor

-- Enable RLS on all tables
ALTER TABLE pillars ENABLE ROW LEVEL SECURITY;
ALTER TABLE areas ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if any (for clean setup)
DROP POLICY IF EXISTS "Users can view own pillars" ON pillars;
DROP POLICY IF EXISTS "Users can insert own pillars" ON pillars;
DROP POLICY IF EXISTS "Users can update own pillars" ON pillars;
DROP POLICY IF EXISTS "Users can delete own pillars" ON pillars;

DROP POLICY IF EXISTS "Users can view own areas" ON areas;
DROP POLICY IF EXISTS "Users can insert own areas" ON areas;
DROP POLICY IF EXISTS "Users can update own areas" ON areas;
DROP POLICY IF EXISTS "Users can delete own areas" ON areas;

DROP POLICY IF EXISTS "Users can view own projects" ON projects;
DROP POLICY IF EXISTS "Users can insert own projects" ON projects;
DROP POLICY IF EXISTS "Users can update own projects" ON projects;
DROP POLICY IF EXISTS "Users can delete own projects" ON projects;

DROP POLICY IF EXISTS "Users can view own tasks" ON tasks;
DROP POLICY IF EXISTS "Users can insert own tasks" ON tasks;
DROP POLICY IF EXISTS "Users can update own tasks" ON tasks;
DROP POLICY IF EXISTS "Users can delete own tasks" ON tasks;

-- PILLARS RLS Policies
CREATE POLICY "Users can view own pillars"
    ON pillars FOR SELECT
    USING (auth.uid()::text = user_id);

CREATE POLICY "Users can insert own pillars"
    ON pillars FOR INSERT
    WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can update own pillars"
    ON pillars FOR UPDATE
    USING (auth.uid()::text = user_id)
    WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can delete own pillars"
    ON pillars FOR DELETE
    USING (auth.uid()::text = user_id);

-- AREAS RLS Policies
CREATE POLICY "Users can view own areas"
    ON areas FOR SELECT
    USING (
        auth.uid()::text = user_id
        OR EXISTS (
            SELECT 1 FROM pillars p
            WHERE p.id = areas.pillar_id
            AND p.user_id = auth.uid()::text
        )
    );

CREATE POLICY "Users can insert own areas"
    ON areas FOR INSERT
    WITH CHECK (
        auth.uid()::text = user_id
        AND EXISTS (
            SELECT 1 FROM pillars p
            WHERE p.id = pillar_id
            AND p.user_id = auth.uid()::text
        )
    );

CREATE POLICY "Users can update own areas"
    ON areas FOR UPDATE
    USING (auth.uid()::text = user_id)
    WITH CHECK (
        auth.uid()::text = user_id
        AND EXISTS (
            SELECT 1 FROM pillars p
            WHERE p.id = pillar_id
            AND p.user_id = auth.uid()::text
        )
    );

CREATE POLICY "Users can delete own areas"
    ON areas FOR DELETE
    USING (auth.uid()::text = user_id);

-- PROJECTS RLS Policies
CREATE POLICY "Users can view own projects"
    ON projects FOR SELECT
    USING (
        auth.uid()::text = user_id
        OR EXISTS (
            SELECT 1 FROM areas a
            WHERE a.id = projects.area_id
            AND a.user_id = auth.uid()::text
        )
    );

CREATE POLICY "Users can insert own projects"
    ON projects FOR INSERT
    WITH CHECK (
        auth.uid()::text = user_id
        AND EXISTS (
            SELECT 1 FROM areas a
            WHERE a.id = area_id
            AND a.user_id = auth.uid()::text
        )
    );

CREATE POLICY "Users can update own projects"
    ON projects FOR UPDATE
    USING (auth.uid()::text = user_id)
    WITH CHECK (
        auth.uid()::text = user_id
        AND EXISTS (
            SELECT 1 FROM areas a
            WHERE a.id = area_id
            AND a.user_id = auth.uid()::text
        )
    );

CREATE POLICY "Users can delete own projects"
    ON projects FOR DELETE
    USING (auth.uid()::text = user_id);

-- TASKS RLS Policies
CREATE POLICY "Users can view own tasks"
    ON tasks FOR SELECT
    USING (
        auth.uid()::text = user_id
        OR EXISTS (
            SELECT 1 FROM projects p
            WHERE p.id = tasks.project_id
            AND p.user_id = auth.uid()::text
        )
    );

CREATE POLICY "Users can insert own tasks"
    ON tasks FOR INSERT
    WITH CHECK (
        auth.uid()::text = user_id
        AND EXISTS (
            SELECT 1 FROM projects p
            WHERE p.id = project_id
            AND p.user_id = auth.uid()::text
        )
    );

CREATE POLICY "Users can update own tasks"
    ON tasks FOR UPDATE
    USING (auth.uid()::text = user_id)
    WITH CHECK (
        auth.uid()::text = user_id
        AND EXISTS (
            SELECT 1 FROM projects p
            WHERE p.id = project_id
            AND p.user_id = auth.uid()::text
        )
    );

CREATE POLICY "Users can delete own tasks"
    ON tasks FOR DELETE
    USING (auth.uid()::text = user_id);

-- Create indexes to support RLS performance
CREATE INDEX IF NOT EXISTS idx_pillars_user_id ON pillars(user_id);
CREATE INDEX IF NOT EXISTS idx_areas_user_id ON areas(user_id);
CREATE INDEX IF NOT EXISTS idx_areas_pillar_id ON areas(pillar_id);
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_area_id ON projects(area_id);
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id);

-- Function to verify RLS is working
CREATE OR REPLACE FUNCTION verify_rls_isolation(test_user_id uuid)
RETURNS TABLE (
    table_name text,
    total_rows bigint,
    user_visible_rows bigint,
    rls_working boolean
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'pillars'::text,
        (SELECT COUNT(*) FROM pillars)::bigint,
        (SELECT COUNT(*) FROM pillars WHERE user_id = test_user_id::text)::bigint,
        (SELECT COUNT(*) FROM pillars) > (SELECT COUNT(*) FROM pillars WHERE user_id = test_user_id::text)
    UNION ALL
    SELECT 
        'areas'::text,
        (SELECT COUNT(*) FROM areas)::bigint,
        (SELECT COUNT(*) FROM areas WHERE user_id = test_user_id::text)::bigint,
        (SELECT COUNT(*) FROM areas) > (SELECT COUNT(*) FROM areas WHERE user_id = test_user_id::text)
    UNION ALL
    SELECT 
        'projects'::text,
        (SELECT COUNT(*) FROM projects)::bigint,
        (SELECT COUNT(*) FROM projects WHERE user_id = test_user_id::text)::bigint,
        (SELECT COUNT(*) FROM projects) > (SELECT COUNT(*) FROM projects WHERE user_id = test_user_id::text)
    UNION ALL
    SELECT 
        'tasks'::text,
        (SELECT COUNT(*) FROM tasks)::bigint,
        (SELECT COUNT(*) FROM tasks WHERE user_id = test_user_id::text)::bigint,
        (SELECT COUNT(*) FROM tasks) > (SELECT COUNT(*) FROM tasks WHERE user_id = test_user_id::text);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;