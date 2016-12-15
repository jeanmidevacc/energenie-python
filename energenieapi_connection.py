from time import time
import datetime
import requests
from requests.auth import HTTPBasicAuth
import json
import pytz
import pandas as pd


# id to connect to the api
user_id={
    "username":"",
    "password":""
}
# header for the http request
header_t={'content-type':'application/json'}
# Requests to interact with the api
REQUEST_LISTSUBDEVICES="https://mihome4u.co.uk/api/v1/device_groups/list"
REQUEST_SUBDEVICESFETCHUSAGEDATA="https://mihome4u.co.uk/api/v1/subdevices/get_data"
# parameters associated to the energenie device
parameters = {"etrv": "reported_temperature",
              "control": "watts",}


tic=time()#tic to estimate the duration

# GET A RAW LIST OF THE DEVICES ASSOCIATED TO THE ACCOUNT  user_id
request_get_listdevice=requests.post(REQUEST_LISTSUBDEVICES,auth=HTTPBasicAuth(user_id["username"],user_id["password"]))
data_c=request_get_listdevice.json()

# Storage of the device in a dictionnary
# {device_id:type of device,}
dict_listdevices={}
for i in range(len(data_c["data"][0]["subdevices"])):
    dict_listdevices[data_c["data"][0]["subdevices"][i]["id"]]=data_c["data"][0]["subdevices"][i]["device_type"]

print(dict_listdevices)






# GET A DATAFRAME THAT CONTAINS THE VALUE FOR THE DEVICES (SMART PLUG AND TRV) ASSOCIATED TO THE ACCOUNT

# The instant historical data is limited to the last 24 hours
start_time = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
end_time=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


for device in dict_listdevices:
    if dict_listdevices[device] in parameters:
        # definition of the parameter to use on the request
        dictparam_pastvalue = {
            "id": device,  # id du sudevice
            "start_time": start_time,
        # start time , start point of the collection of the historical data in this case 24 hours ago
            "end_time":end_time,
        # end_time , end point of the historical data in this case now
            "resolution": "instant",  # resolution instant to obtain the last instant measurements
            "data_type": parameters[dict_listdevices[device]],
        # data_type , parameter to collect the measurement could be watts (for the smart plug) of reported_temperature (for the smart trv)
            "limit": 86400  # limit , maximal number of points to collect
        }

        # POST Request to obtain the historical data
        request_get_historicalinstantdata = requests.post(REQUEST_SUBDEVICESFETCHUSAGEDATA,
                                                          auth=requests.auth.HTTPBasicAuth(user_id["username"],
                                                                                           user_id["password"]),
                                                          data=json.dumps(dictparam_pastvalue), headers=header_t)
        # Storage of the data
        data_api= request_get_historicalinstantdata.json()
        raw_data=data_api["data"]


        # Definiton of a dataframe that contains in index the local timestamp of the measure , and the value in the column

        list_df = []
        list_tstp=[]
        for row in raw_data:
            date_object = datetime.datetime.strptime(row[0], "%Y-%m-%dT%H:%M:%S.000Z")
            list_df.append(row[1])
            list_tstp.append(date_object)

        df=pd.DataFrame(list_df,index=list_tstp,columns=["value"])
        print(df)


toc=time()-tic
print("EXECUTION_TIME(s):"+str(toc))
print("STOP")
