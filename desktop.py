import webview
from threading import Thread
from app import app  # Tera main Flask file (app.py) import kar

if __name__ == '__main__':
    # Flask ko background mein chala
    t = Thread(target=app.run, kwargs={'debug': False, 'use_reloader': False, 'port': 5000})
    t.daemon = True
    t.start()

    # Desktop window khol (tera app browser jaisa dikhega)
    webview.create_window(
        title='Tailor Management System',
        url='http://127.0.0.1:5000',
        width=1200,
        height=800,
        resizable=True,
        # Icon agar daalna hai to:
        # icon='static/icon.ico'   ← pehle .ico file bana ke yahan path daal
    )
    webview.start()