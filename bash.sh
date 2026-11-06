#!/bin/bash
set -e
cd "$(dirname "$0")"
export PORT="${PORT:-${WEBSITES_PORT:-8000}}"
export API_PORT="${API_PORT:-8001}"
export API_BASE_URL="http://127.0.0.1:${API_PORT}"

if ! ldconfig -p 2>/dev/null|grep -q libodbc.so; then
    SUDO=""
    if [ "$(id -u)" -ne 0 ]; then SUDO="sudo"; fi
    $SUDO apt-get update
    $SUDO apt-get install -y unixodbc unixodbc-dev
fi

if [ -d "antenv" ]; then
    source antenv/bin/activate
fi
pip install --no-cache-dir -r requirements.txt

python -m uvicorn api_app:app --host 127.0.0.1 --port "$API_PORT"&

for i in $(seq 120);do
 if python -c "import socket;socket.create_connection(('127.0.0.1',$API_PORT),1)" 2>/dev/null; then
     break
 fi
 sleep 1
done

exec python app.py
