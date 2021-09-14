from watchdog.events import FileSystemEventHandler
from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer
import asyncio
import logging
import time


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    path = "/home/reven_n1/Projects/Python/Bots/DiscordBot/library"

    even_handler = LoggingEventHandler()

    observer = Observer()
    observer.schedule(even_handler, path, recursive=True)

    observer.start()

    try:
        while True:
            await asyncio.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

# class Handler(FileSystemEventHandler):
#     def on_created(self, event):
#         print event

#     def on_deleted(self, event):
#         print event

#     def on_moved(self, event):
#         print event

if __name__ == "__main__":
    asyncio.run(main())