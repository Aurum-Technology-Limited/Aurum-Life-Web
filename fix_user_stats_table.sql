-- Fix user_stats table - add missing updated_at column
ALTER TABLE public.user_stats 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Add trigger for updated_at
CREATE OR REPLACE FUNCTION update_user_stats_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_user_stats_updated_at ON public.user_stats;
CREATE TRIGGER update_user_stats_updated_at 
    BEFORE UPDATE ON public.user_stats 
    FOR EACH ROW EXECUTE FUNCTION update_user_stats_updated_at();