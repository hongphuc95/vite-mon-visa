import time
import os
from planning import run

if __name__ == '__main__':
    refresh_time = int(os.environ.get("REFRESH_TIME", 300))

    starttime = time.time()
    while True:
        run()
        time.sleep(refresh_time - ((time.time() - starttime) % refresh_time))