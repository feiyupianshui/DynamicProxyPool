
from proxypool.api import app
from proxypool.schedule import Schedule

def main():
    s = Schedule()
    app.run()
    s.run()

if __name__ == '__main__':
    main()