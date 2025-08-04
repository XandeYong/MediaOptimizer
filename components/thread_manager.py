import threading
import time

# Get the number of active threads
print(f"Active Threads: {threading.active_count()}")

# List all running threads
for thread in threading.enumerate():
    print(thread.name)


# in-progress