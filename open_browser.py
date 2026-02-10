#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для открытия index.html в браузере через локальный веб-сервер.
Если рядом лежит index.html.br (Brotli), сервер отдает его с заголовком
Content-Encoding: br, а браузер сам расшифровывает страницу.
"""
import os
import webbrowser
import http.server
import socketserver
import threading
import time
from pathlib import Path

PORT = 8000


class BrotliIndexHandler(http.server.SimpleHTTPRequestHandler):
    """Обработчик, который для / и /index.html отдает index.html.br (если есть)."""

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            base_dir = Path(os.getcwd())
            br_path = base_dir / "index.html.br"

            if br_path.exists():
                try:
                    with br_path.open("rb") as f:
                        data = f.read()

                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Encoding", "br")
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
                except Exception as e:
                    print(f"Ошибка отдачи Brotli-файла: {e}")
                    # если не получилось – пускаем дальше в стандартный обработчик

        # все остальные запросы (и fallback) – обычная статика
        super().do_GET()


def start_server(directory: str) -> None:
    """Запускает локальный HTTP сервер"""
    os.chdir(directory)
    handler = BrotliIndexHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    print(f"Сервер запущен на http://localhost:{PORT}")
    httpd.serve_forever()


def open_html_in_browser() -> None:
    """Открывает index.html (или index.html.br) в браузере через локальный сервер."""
    script_dir = Path(__file__).parent

    html_file = script_dir / "index.html"
    br_file = script_dir / "index.html.br"

    if not html_file.exists() and not br_file.exists():
        print(f"Ошибка: ни {html_file.name}, ни {br_file.name} не найдены в {script_dir}!")
        return

    # Запускаем сервер в отдельном потоке
    server_thread = threading.Thread(
        target=start_server,
        args=(str(script_dir),),
        daemon=True,
    )
    server_thread.start()

    # Ждем немного, чтобы сервер успел запуститься
    time.sleep(1)

    # Открываем в браузере
    url = f"http://localhost:{PORT}/index.html"
    print("Открываю страницу в браузере...")
    print(f"URL: {url}")
    print("\nСервер работает. Нажмите Ctrl+C для остановки.")
    webbrowser.open(url)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nОстановка сервера...")


if __name__ == "__main__":
    open_html_in_browser()
