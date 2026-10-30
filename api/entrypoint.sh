#!/bin/sh
set -e

# Run seed script if the database doesn't have articles yet
# The seed.py script already checks if articles exist
python3 seed.py || true

# Start the API server
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
