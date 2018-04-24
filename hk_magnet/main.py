
from hk_magnet.localtime_api import *
import time
## Check Time:
## A 00:00:00 - 09:15:00 wait for starting
## B 09:15:00 - 09:31:00 can start to work
## C 09:31:00 - 23:59:59 cannot start to work

## Actions
## A
## Loop wait for 5mins and check
## B
## Start
## C
## Loop wait for 5 mins , never start


TIME_CMP_BIGGER = 1
TIME_CMP_EQUAL = 0
TIME_CMP_SMALLER = -1

RET_OK = 0
RET_ERR = -1

TIME_ACTIVE_LEFT = '09:16:00'
TIME_ACTIVE_RIGHT = '09:31:00'
TIME_WORK_DONE = '09:45:00'

#TIME_ACTIVE_LEFT = '20:56:00'
#TIME_ACTIVE_RIGHT = '21:11:00'
#TIME_WORK_DONE = '21:25:00'


class main_control:
    def __init__(self):
        pass

    def srv_start(self):
        print("Start Server")
        while True:
            while True:
                local_time = self.get_local_time()
                if (self.compare_time(local_time, TIME_ACTIVE_RIGHT) == TIME_CMP_SMALLER or self.compare_time(local_time,
                                                                                                            TIME_ACTIVE_RIGHT) == TIME_CMP_EQUAL) and \
                                self.compare_time(local_time, TIME_ACTIVE_LEFT) == TIME_CMP_BIGGER:
                    break
                else:
                    print(">")
                    time.sleep(150)
                    continue
            print("Start Work")
            self.fake_work_success()
            print("Finish Work")
            while True:
                if self.compare_time(local_time, TIME_ACTIVE_LEFT) == TIME_CMP_BIGGER:
                    break
                else:
                    print("<")
                    time.sleep(150)
                    continue

        print("Stop Server")

    def srv_stop(self):
        pass

    def get_local_time(self):
        l = localtime_api()
        return l.get_local_time()

    def get_local_date(self):
        l = localtime_api()
        return l.get_local_date()

    def compare_time(self, a_time, b_time):
        a_time_list = a_time.split(":")
        a_time_list_second = int(a_time_list[0]) * 3600 + \
                             int(a_time_list[1]) * 60 + \
                             int(a_time_list[2]) * 1
        b_time_list = b_time.split(":")
        b_time_list_second = int(b_time_list[0]) * 3600 + \
                             int(b_time_list[1]) * 60 + \
                             int(b_time_list[2]) * 1

        if a_time_list_second > b_time_list_second:
            return TIME_CMP_BIGGER
        elif a_time_list_second == b_time_list_second:
            return TIME_CMP_EQUAL
        else:
            return TIME_CMP_SMALLER

    ## Exit when 09:45:00
    def fake_work_success(self):
        while True:
            local_time = self.get_local_time()
            if self.compare_time(local_time, TIME_WORK_DONE) == TIME_CMP_BIGGER or self.compare_time(local_time, TIME_WORK_DONE) == TIME_CMP_EQUAL:
                break
            else:
                time.sleep(2)
                continue
        return

    ## sleep for 3 seconds
    def fake_work_fails(self):
        time.sleep(5)
        return

if __name__ == "__main__":
    mc = main_control()
    mc.srv_start()