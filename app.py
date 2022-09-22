from threading import main_thread
import time
from planning import run

if __name__ == '__main__':
    refresh_time = 300 # 5min refresh
    while True:
        run()
        time.sleep(refresh_time)
