import time
import os
from planning import run

if __name__ == '__main__':
    if os.environ.get("REFRESH_TIME"):
        refresh_time = int(os.environ.get("REFRESH_TIME"))
    else:
        refresh_time = 180

    starttime = time.time()
    while True:
        run()
        time.sleep(refresh_time - ((time.time() - starttime) % refresh_time))