from api import app
from schedule import Schedule

def main():

    s = Schedule()
    s.run()
    app.run()




if __name__ == '__main__':
    main()

