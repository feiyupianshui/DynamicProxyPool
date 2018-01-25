
from proxypool.scheduler import Scheduler
import sys
import io

def main():
    try:
        s = Scheduler()
        s.run()
    except:
        main()


if __name__ == '__main__':
    main()