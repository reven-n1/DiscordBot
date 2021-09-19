from importlib import reload 
import watchdog.observers
import watchdog.events
import asyncio


class Handler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self):
        watchdog.events.PatternMatchingEventHandler.__init__(self, patterns=["*.py", "*.json"], ignore_patterns = None,
                                                     ignore_directories = False, case_sensitive = True)

    def on_created(self, event):
        print(f"File was created at {event.src_path}")
        

    def on_deleted(self, event):
        print(f"File was deleted at {event.src_path}")

    

    def on_modified(self, event):
        print(f"File was modified at {event.src_path}")


async def main():
    event_handler = Handler()
    observer = watchdog.observers.Observer()
    observer.schedule(event_handler, r"/home/reven_n1/Projects/Python/Bots/DiscordBot/library", recursive = True)
    observer.start()
    observer.join()
    

if __name__ == "__main__":
    asyncio.run(main())