import json
from datetime import datetime, timedelta

file_path = '/home/pi/buddylist-files/'
with open(file_path+'node-archive.txt', 'r') as file:
    node_list = json.load(file)

new_node_list = {}

for i in node_list:
    new_node_list[i] = {}
    new_node_list[i]["ID"] = node_list[i]["ID"]
    new_node_list[i]["Short Name"] = node_list[i]["Short Name"]
    new_node_list[i]["Long Name"] = node_list[i]["Long Name"]
    new_node_list[i]["AKA"] = node_list[i]["AKA"]
    new_node_list[i]["Hardware"] = node_list[i]["Hardware"]
    new_node_list[i]["Latitude"] = node_list[i]["Latitude"]
    new_node_list[i]["Longitude"] = node_list[i]["Longitude"]
    new_node_list[i]["Altitude"] = node_list[i]["Altitude"]
    new_node_list[i]["Hops Away"] = node_list[i]["Hops Away"]
    new_node_list[i]["Channel"] = node_list[i]["Channel"]
    new_node_list[i]["Times Heard"] = [node_list[i]["Times Heard"][0], node_list[i]["Times Heard"][-1]]
    
#print(new_node_list)
with open(file_path+'node-archive-'+datetime.now().strftime("%Y-%m-%d")+'.txt', 'w') as f:
    json.dump(node_list, f, indent=4)
    
with open(file_path+'node-archive.txt', 'w') as f:
    json.dump(new_node_list, f, indent=4)