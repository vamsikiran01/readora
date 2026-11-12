#!/bin/bash
# Build script executed by Vercel upon deployment
echo "🚀 Installing Python dependencies..."
python3 -m pip install -r requirements.txt

echo "📦 Collecting static files..."
python3 manage.py collectstatic --noinput --clear

echo "✅ Build completed successfully!"
