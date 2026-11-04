#!/usr/bin/env python3
"""lanshare - share a folder over Wi-Fi. Open the printed URL on your phone to
browse/download files, or upload files from the phone to this computer.

Usage:
    python lanshare.py              # share current folder on port 8000
    python lanshare.py D:/Movies -p 9000
Only use on networks you trust: anyone on the LAN can read and upload.
"""
import argparse
import functools
import html
import http.server
import io
import os
import re
import socket
from urllib.parse import quote, unquote

PAGE = """<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>lanshare</title><style>body{{font:18px sans-serif;margin:1em}}li{{margin:.4em 0}}</style>
<h2>{title}</h2><ul>{items}</ul><hr><form method="post" enctype="multipart/form-data">
<input type="file" name="f" multiple> <button>Upload</button></form>"""


def lan_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("10.255.255.255", 1))  # no packet is sent
            return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"


def parse_multipart(body, boundary):
    """Yield (filename, data) for every uploaded file in a multipart body."""
    for part in body.split(b"--" + boundary):
        m = re.search(rb'filename="([^"]+)"[^\r\n]*\r\n(?:[^\r\n]+\r\n)*\r\n', part)
        if m:
            name = os.path.basename(m.group(1).decode("utf-8", "replace").replace("\\", "/"))
            yield name, part[m.end():-2]  # strip trailing \r\n


class Handler(http.server.SimpleHTTPRequestHandler):
    def list_directory(self, path):
        names = sorted(os.listdir(path), key=str.lower)
        slash = lambda n: "/" if os.path.isdir(os.path.join(path, n)) else ""
        items = "".join(f'<li><a href="{quote(n)}{slash(n)}">{html.escape(n)}{slash(n)}</a>' for n in names)
        data = PAGE.format(title=html.escape(unquote(self.path)), items=items).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        return io.BytesIO(data)

    def do_POST(self):
        boundary = self.headers.get("Content-Type", "").split("boundary=")[-1].encode()
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        folder = self.translate_path(self.path)
        saved = 0
        for name, data in parse_multipart(body, boundary):
            with open(os.path.join(folder, name), "wb") as f:
                f.write(data)
            saved += 1
        self.send_response(303)
        self.send_header("Location", self.path)
        self.end_headers()
        self.log_message("uploaded %d file(s)", saved)


def main():
    ap = argparse.ArgumentParser(description="Share a folder on your local network.")
    ap.add_argument("folder", nargs="?", default=".")
    ap.add_argument("-p", "--port", type=int, default=8000)
    args = ap.parse_args()
    folder = os.path.abspath(args.folder)
    server = http.server.ThreadingHTTPServer(("0.0.0.0", args.port), functools.partial(Handler, directory=folder))
    print(f"Sharing {folder}\nOpen on your phone: http://{lan_ip()}:{args.port}\nCtrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
