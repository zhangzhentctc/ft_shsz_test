from datetime import *

class localtime_api:
    def __init__(self):
        pass

    def get_local_time(self):
        now_time = datetime.now()
        now_time_str = datetime.strftime(now_time, '%Y-%m-%d %H:%M:%S')
        localtime = now_time_str.split(' ')[1]
        return localtime

    def get_local_date(self):
        now_time = datetime.now()
        now_time_str = datetime.strftime(now_time, '%Y-%m-%d %H:%M:%S')
        localdate = now_time_str.split(' ')[0]
        return localdate


##### TEST
if __name__ == "__main__":
    l = localtime_api()
    print(l.get_local_time())
    print(l.get_local_date())


