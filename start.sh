#!/bin/bash
echo "🚀 Starting A-Wave Background SOC Engines..."
python run_soc_engines.py &

echo "🌐 Starting Flask API Web Server..."
python backend/app.py