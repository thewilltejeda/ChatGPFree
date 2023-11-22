import webview
from threading import Thread, Event
from main import app  # Assuming app.py is your Flask application

# This event will be set when we need to stop the Flask server
stop_event = Event()

app_title = "OwnAI"
host = "http://127.0.0.1"
port = 9898

def run():
    while not stop_event.is_set():
        app.run(port=port, use_reloader=False)

if __name__ == '__main__':
    t = Thread(target=run)
    t.daemon = True  # This ensures the thread will exit when the main program exits
    t.start()

    width = 400
    height= 400

    webview.create_window(
        app_title,
        f"{host}:{port}",
        text_select=True,
        confirm_close=True,
        # resizable=False,
        #height=710,
        x=1920-width,
        y=0,
        height=height,
        width=width,
        min_size=(400, 400),
        frameless=True,
        #easy_drag=True,
        on_top=True
        )
    
    webview.start()

    stop_event.set()  # Signal the Flask server to shut down
