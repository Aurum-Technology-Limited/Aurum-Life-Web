-- Add birth_date field to user_profiles table
ALTER TABLE public.user_profiles 
ADD COLUMN IF NOT EXISTS birth_date DATE;

-- Update existing users with random birth dates (ages 22-45)
UPDATE public.user_profiles 
SET birth_date = (
    CURRENT_DATE - INTERVAL '1 year' * (22 + floor(random() * 24)::int) - INTERVAL '1 day' * floor(random() * 365)::int
)
WHERE birth_date IS NULL;

-- Add index for potential age-based queries
CREATE INDEX IF NOT EXISTS idx_user_profiles_birth_date ON user_profiles(birth_date);