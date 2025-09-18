-- Create system user for journal templates and other system-level entities
INSERT INTO public.users (
    id,
    username,
    email,
    first_name,
    last_name,
    is_active,
    level,
    total_points,
    current_streak
) VALUES (
    '00000000-0000-0000-0000-000000000000',
    'system',
    'system@aurumlife.internal',
    'System',
    'User',
    true,
    1,
    0,
    0
) ON CONFLICT (id) DO NOTHING;