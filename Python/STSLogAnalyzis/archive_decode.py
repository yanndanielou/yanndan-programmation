import json

# JSON string
json_data = '{"SQLARCH":{"caller":"","catAla":0,"eqp":"PAS 05","eqpId":"EQ_PAS_05_PAS_05","exeSt":"","id":"M_PAS_05_ZC_ATS_TRACKING_STATUS_TRAINS_ID","jdb":false,"label":"PAS_05 : ZC ATS TRACKING STATUS TRAINS ID [161]","loc":"PAS 05","locale":"2025-07-21T10:54:18.439+02:00","newSt":"14 09 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 04 E4 44 00 01 19 40 27 EC ","oldSt":"","orders":"","sigT":"TSA","tstamp":"2025-07-21T10:54:18.000+02:00","utc_locale":"2025-07-21T08:54:18.439+01:00"},"date":"2025-07-21T10:54:18.440+02:00","tags":["SQLARCH"]}'

# Parsing JSON string
data = json.loads(json_data)

# Accessing data
sqlarch = data["SQLARCH"]
date = data["date"]
tags = data["tags"]

print("SQLARCH:", sqlarch)
print("Date:", date)
print("Tags:", tags)
