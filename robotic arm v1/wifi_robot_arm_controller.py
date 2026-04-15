import requests
import time 

default_p1  = [-50.0, 50.0, -20.0]
default_p2 = [45.0, 50.0, -20.0]

open_gripper_url = "http://192.168.4.1/gripper?action=open"
close_gripper_url = "http://192.168.4.1/gripper?action=close"

# for i in range(10):
#     res=requests.get(open_gripper_url,timeout=10)
#     time.sleep(1)
#     res=requests.get(close_gripper_url,timeout=10)
#     time.sleep(1)


# res = requests.post("http://192.168.4.1/stepper?num=1&angle=-50", timeout=10)
# res = requests.post("http://192.168.4.1/stepper?num=2&angle=50", timeout=10)
# res = requests.post("http://192.168.4.1/stepper?num=3&angle=-20", timeout=10)
# res = requests.post("http://192.168.4.1/stepper?num=1&angle=45", timeout=10)
# res = requests.post("http://192.168.4.1/stepper?num=2&angle=50", timeout=10)
# res = requests.post("http://192.168.4.1/stepper?num=3&angle=-20", timeout=10)


# res=requests.post(open_gripper_url)
# res=requests.post(close_gripper_url)
# res = requests.post("http://192.168.4.1/calibrate", timeout=10)
