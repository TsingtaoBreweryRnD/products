#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品信息库本地服务器
功能：
  1. 提供静态文件（index.html / products.json / 图片等）
  2. 提供 POST /api/save 接口，把前端编辑后的数据写回 products.json

启动方式（在终端里，先进入本文件夹，然后运行）：
    python3 server.py
之后浏览器打开 http://localhost:8000 （直接显示主页面）。
保持这个终端窗口开启；按 Ctrl+C 停止服务器。
"""
import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_FILE = os.path.join(BASE_DIR, "products.json")
PORT = 8000


class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/api/save":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length).decode("utf-8")
                data = json.loads(raw)
                if not isinstance(data, list):
                    raise ValueError("数据必须是 JSON 数组")
                # 原子写入：先写临时文件再替换，避免写一半损坏文件
                tmp = PRODUCTS_FILE + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    f.write("\n")
                os.replace(tmp, PRODUCTS_FILE)
                self._send_json(200, {"ok": True, "count": len(data)})
            except Exception as e:
                self._send_json(500, {"ok": False, "error": str(e)})
        else:
            self._send_json(404, {"ok": False, "error": "未找到该接口"})

    def _send_json(self, code, obj):
        payload = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    print("=" * 46)
    print("  产品信息库本地服务器已启动")
    print("  请在浏览器打开: http://localhost:%d" % PORT)
    print("  保持本窗口开启；按 Ctrl+C 停止服务器")
    print("=" * 46)
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
