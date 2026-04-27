#!/usr/bin/env python3
"""
陌拜地图 HTTP 服务器
- 静态文件服务（局域网手机/电脑均可访问）
- 高德地图 JS API 从 CDN 加载，无需服务器提供 HTTPS
"""
import json, os, socket
from http.server import HTTPServer, BaseHTTPRequestHandler

HOST = "0.0.0.0"
PORT = 7823
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "records.json")

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"  {args[0]}")

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.serve_file("/index.html", "text/html; charset=utf-8")
        elif self.path == "/manifest.json":
            self.serve_file("/manifest.json", "application/json")
        elif self.path == "/sw.js":
            self.serve_file("/sw.js", "application/javascript")
        elif self.path.startswith("/icon-"):
            self.serve_file(self.path, "image/png")
        elif self.path == "/api/records":
            self.serve_records()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/api/sync":
            self.handle_sync()
        else:
            self.send_error(404)

    def serve_file(self, path, content_type):
        filepath = BASE + path
        if os.path.exists(filepath):
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_cors_headers()
            self.end_headers()
            with open(filepath, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)

    def serve_records(self):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = []
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def handle_sync(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            payload = json.loads(body)
            records = payload.get("records", [])

            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "count": len(records)}).encode("utf-8"))
            print(f"  [同步] 保存 {len(records)} 条记录 ✓")
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

def get_lan_ip():
    """获取本机局域网IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def run():
    server = HTTPServer((HOST, PORT), Handler)
    local_ip = get_lan_ip()
    print(f"🗺️  陌拜地图服务器已启动")
    print(f"   📱 手机访问:  http://{local_ip}:{PORT}")
    print(f"   💻 电脑访问:  http://localhost:{PORT}")
    print(f"   ⚠️  注意：同一WiFi网络下才能访问")
    print(f"   按 Ctrl+C 停止\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
        server.shutdown()

if __name__ == "__main__":
    run()
