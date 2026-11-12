#!/bin/bash
echo "🚀 BUILD START"

# Create a virtual environment to isolate pip and python
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install requirements in virtualenv
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# Run collectstatic with the virtualenv Python
python3 manage.py collectstatic --noinput --clear

echo "✅ BUILD END"
