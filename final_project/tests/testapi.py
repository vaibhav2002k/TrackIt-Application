import requests
import datetime

baseurl =  "http://192.168.43.212:8080/api/"

# log_data = {"timestamp": datetime.datetime(2022,12,16,5,2,12), "value":0}
tracker_data = {"name": "apitest3", "description":"new description", "tracker_type":"mct"
, "settings":"1,2,3,4", }

# response = requests.get(baseurl + "user/vaibhav1")
response = requests.put(baseurl + "tracker/10", tracker_data)
# response = requests.post(baseurl + "user", {"username": "apitest"})
# response = requests.delete(baseurl + "user/vaibhav")

print(response.json())