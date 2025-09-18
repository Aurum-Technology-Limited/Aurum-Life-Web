#!/bin/bash
# Analytics Tables Migration Script
# Run this from the /app/backend directory

echo "🚀 Starting Aurum Life Analytics Tables Migration"
echo "=================================================="

# Check if Python environment is ready
echo "🔍 Checking Python environment..."
python3 -c "import supabase, dotenv" 2>/dev/null || {
    echo "❌ Missing required packages. Installing..."
    pip install supabase python-dotenv
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY"
    exit 1
fi

echo "✅ Environment ready"
echo ""

# Run the migration
echo "📋 Executing analytics tables migration..."
python3 run_analytics_migrations.py

echo ""
echo "🔍 Verifying tables after migration..."
python3 verify_analytics_tables.py

echo ""
echo "🎉 Analytics migration process complete!"
echo "Check the logs above for any errors or warnings"