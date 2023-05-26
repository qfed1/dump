import pandas as pd
from pathlib import Path
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == str(file_path):
            process_file()


def process_file():
    df = pd.read_csv(file_path, header=None, dtype=str)
    df['concat'] = df.apply(lambda row: ' '.join(row.dropna()), axis=1)
    df['concat'].to_frame('Concatenated').to_csv('outputvolume.csv', index=False)


file_path = Path(r"C:\Users\evanb\git\AI\NEWFILES\messagesvolume.csv")

event_handler = FileChangeHandler()
observer = Observer()
observer.schedule(event_handler, path=str(file_path.parent), recursive=False)

process_file()  # process the file initially

observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
