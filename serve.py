#!/usr/bin/env python3
"""Simple HTTP server for web_nav_v2"""
import http.server
import socketserver
import os
import json
from urllib.parse import urlparse, parse_qs

PORT = 8080
WEB_ROOT = os.path.dirname(os.path.abspath(__file__))

class WebNavHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_ROOT, **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def do_GET(self):
        # Serve data/websites.json
        if self.path == '/data/websites.json':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            with open(os.path.join(WEB_ROOT, 'data', 'websites.json'), 'rb') as f:
                self.wfile.write(f.read())
            return

        # Serve favicon.ico from images
        if self.path == '/favicon.ico':
            self.send_response(200)
            self.send_header('Content-Type', 'image/x-icon')
            self.end_headers()
            favicon_path = os.path.join(WEB_ROOT, 'favicon.ico')
            if os.path.exists(favicon_path):
                with open(favicon_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                with open(os.path.join(WEB_ROOT, 'assets', 'images', 'favicon.png'), 'rb') as f:
                    self.wfile.write(f.read())
            return

        # Serve Tailwind CSS locally if CDN fails
        if self.path == '/tailwind.css':
            self.send_response(200)
            self.send_header('Content-Type', 'text/css')
            self.end_headers()
            tailwind = """
            @tailwind base;
            @tailwind components;
            @tailwind utilities;
            /* Fallback utility classes */
            .bg-gray-50 { background-color: #f9fafb; }
            .bg-white { background-color: #ffffff; }
            .text-gray-800 { color: #111827; }
            .text-gray-400 { color: #9ca3af; }
            .text-gray-600 { color: #4b5563; }
            .border-gray-200 { border-color: #e5e7eb; }
            .bg-gray-100 { background-color: #f3f4f6; }
            .hover\\:bg-gray-100:hover { background-color: #f3f4f6; }
            .focus\\:bg-white:focus { background-color: #ffffff; }
            .focus\\:border-blue-500:focus { border-color: #3b82f6; }
            .focus\\:ring-2:focus { outline: 2px solid transparent; }
            .focus\\:ring-blue-100:focus { --tw-ring-color: #dbeafe; }
            .rounded-xl { border-radius: 0.5rem; }
            .rounded-lg { border-radius: 0.375rem; }
            .pl-10 { padding-left: 2.5rem; }
            .pr-10 { padding-right: 2.5rem; }
            .py-2\\.5 { padding-top: 0.625rem; padding-bottom: 0.625rem; }
            .py-3 { padding-top: 0.75rem; padding-bottom: 0.75rem; }
            .py-4 { padding-top: 1rem; padding-bottom: 1rem; }
            .px-4 { padding-left: 1rem; padding-right: 1rem; }
            .max-w-7xl { max-width: 80rem; }
            .mx-auto { margin-left: auto; margin-right: auto; }
            .flex { display: flex; }
            .justify-between { justify-content: space-between; }
            .items-center { align-items: center; }
            .gap-4 { gap: 1rem; }
            .gap-6 { gap: 1.5rem; }
            .w-full { width: 100%; }
            .max-w-md { max-width: 28rem; }
            .ml-auto { margin-left: auto; }
            .relative { position: relative; }
            .absolute { position: absolute; }
            .left-0 { left: 0px; }
            .right-0 { right: 0px; }
            .top-0 { top: 0px; }
            .top-16 { top: 4rem; }
            .bottom-0 { bottom: 0px; }
            .-translate-x-full { --tw-translate-x: -100%; transform: translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)); }
            .lg\\:translate-x-0 { @media (min-width: 1024px) { --tw-translate-x: 0px; } }
            .lg\\:w-64 { @media (min-width: 1024px) { width: 16rem; } }
            .lg\\:sticky { @media (min-width: 1024px) { position: sticky; } }
            .lg\\:hidden { @media (min-width: 1024px) { display: none; } }
            .lg\\:shadow-none { @media (min-width: 1024px) { --tw-shadow: 0 0 #0000; box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-shadow, 0 0 #0000), var(--tw-shadow, 0 0 #0000); } }
            .shadow-sm { --tw-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05); box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-shadow, 0 0 #0000), var(--tw-shadow, 0 0 #0000); }
            .shadow-xl { --tw-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1); box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-shadow, 0 0 #0000), var(--tw-shadow, 0 0 #0000); }
            .sticky { position: sticky; }
            .z-40 { z-index: 40; }
            .z-50 { z-index: 50; }
            .overflow-hidden { overflow: hidden; }
            """
            self.wfile.write(tailwind.encode())
            return

        # Serve static files
        if self.path == '/' or self.path == '':
            self.path = '/index.html'

        return super().do_GET()

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), WebNavHandler) as httpd:
        print(f"Serving web_nav_v2 at http://localhost:{PORT}")
        httpd.serve_forever()
