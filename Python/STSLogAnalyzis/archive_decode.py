import json

# JSON string
json_data = '{"SQLARCH":{"caller":"","catAla":0,"eqp":"PAS 05","eqpId":"EQ_PAS_05_PAS_05","exeSt":"","id":"M_PAS_05_ZC_ATS_TRACKING_STATUS_TRAINS_ID","jdb":false,"label":"PAS_05 : ZC ATS TRACKING STATUS TRAINS ID [161]","loc":"PAS 05","locale":"2025-07-21T10:54:18.439+02:00","newSt":"14 09 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 04 E4 44 00 01 19 40 27 EC ","oldSt":"","orders":"","sigT":"TSA","tstamp":"2025-07-21T10:54:18.000+02:00","utc_locale":"2025-07-21T08:54:18.439+01:00"},"date":"2025-07-21T10:54:18.440+02:00","tags":["SQLARCH"]}'

# Parsing JSON string
data = json.loads(json_data)

# Directly copy all items from SQLARCH section into a new dictionary
sqlarch_fields = data.get("SQLARCH", {})

# Access global fields
date = data["date"]
tags = data["tags"]


# Accessing specific fields
sqlarch = data["SQLARCH"]
caller = sqlarch.get("caller")
catAla = sqlarch.get("catAla")
eqp = sqlarch.get("eqp")
eqpId = sqlarch.get("eqpId")
exeSt = sqlarch.get("exeSt")
id_field = sqlarch.get("id")
jdb = sqlarch.get("jdb")
label = sqlarch.get("label")
loc = sqlarch.get("loc")

# Print extracted fields
print("Caller:", caller)
print("CatAla:", catAla)
print("Eqp:", eqp)
print("EqpId:", eqpId)
print("ExeSt:", exeSt)
print("ID:", id_field)
print("Jdb:", jdb)
print("Label:", label)
print("Loc:", loc)


# Print the dictionary for SQLARCH fields
for key, value in sqlarch_fields.items():
    print(f"{key}: {value}")

print("Date:", date)
print("Tags:", tags)
