set -e
cd "$(dirname "$0")"
export PORT = "${PORT:-${WEBSITES_PORT:-8000}}"
export API_PORT = "${API_PORT:-8001}"
export API_BASE_URL = "http://127.0.0.1:${API_PORT}"

if [-d "antenv"]: then
    source antenv/bin/activate
fi
python -c "import fastmcp" 2>/dev/null || pip install --no-cache-dir -r requirements.txt

python -m uvicorn api_app:app --host 127.0.0.1 --port "$API_PORT"&

for i in $(seq 120); do
 python -c "import socket; socket.create_connection(('127.0.0.1',$API_PORT),1)"2>/dev/null && break
 sleep 1
done

exec python mcp_server.py