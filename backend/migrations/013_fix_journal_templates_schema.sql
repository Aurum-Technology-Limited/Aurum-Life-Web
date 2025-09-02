-- Migration 013: Fix journal_templates table schema
-- Add missing 'deleted' column for soft delete functionality

-- Check if journal_templates table exists, if not create it
DO $$
BEGIN
    -- Create journal_templates table if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'journal_templates') THEN
        CREATE TABLE journal_templates (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            template_type VARCHAR(50) DEFAULT 'custom',
            structure JSONB DEFAULT '[]',
            prompts JSONB DEFAULT '[]',
            tags JSONB DEFAULT '[]',
            is_default BOOLEAN DEFAULT false,
            is_shared BOOLEAN DEFAULT false,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            deleted BOOLEAN DEFAULT false
        );
        
        -- Add RLS policies
        ALTER TABLE journal_templates ENABLE ROW LEVEL SECURITY;
        
        -- Policy for users to see their own templates
        CREATE POLICY "Users can see their own journal templates"
        ON journal_templates FOR ALL
        USING (auth.uid() = user_id);
        
        RAISE NOTICE 'Created journal_templates table with all required columns';
    ELSE
        -- Table exists, check if 'deleted' column exists
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'journal_templates' AND column_name = 'deleted') THEN
            ALTER TABLE journal_templates ADD COLUMN deleted BOOLEAN DEFAULT false;
            RAISE NOTICE 'Added missing deleted column to journal_templates table';
        ELSE
            RAISE NOTICE 'journal_templates table already has deleted column';
        END IF;
    END IF;
END
$$;