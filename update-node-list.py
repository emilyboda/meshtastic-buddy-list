import subprocess
import re
from tabulate import tabulate
import json
from datetime import datetime, timedelta

file_path = '/home/pi/buddylist-files/'
path_to_venv = '/home/pi/buddylist/'

def run_meshtastic_nodes():
    parsed_data = []
    try:
        # Run the bash command 'meshtastic --nodes'
        result = subprocess.run([path_to_venv + 'bin/meshtastic', '--nodes'], capture_output=True, text=True)
        
        # Check if the command was successful
        if result.returncode == 0:
            print("Command executed successfully.")
            for line in result.stdout.split('\n'):
                # format the command output into an array
                # Use regex to find data between '│' symbols and strip excess spaces
                row_data = re.findall(r"\│\s*([^│]+?)\s*(?=\│)", line)
                if row_data:
                    parsed_data.append([item.strip() for item in row_data])
        
            # Insert the "AKA" column after "Short Name" by calculating it from "ID"
            for row in parsed_data[1:]:
                aka_value = "Meshtastic " + row[2][-4:]  # Take the last 4 digits of the "ID" column (index 2)
                row.insert(4, aka_value)  # Insert the AKA value at the 4th position

            # Define headers for the table 
            headers = ["N", "Long Name", "ID", "Short Name", "AKA", "Hardware", "Latitude", "Longitude", "Altitude", "Battery", 
                       "Channel Util.", "Tx Air Util.", "SNR", "Hops Away", "Channel", "LastHeard", "Since"]

            # Print the parsed data in a formatted table using tabulate, starting from the second row
            #print(tabulate(parsed_data[1:], headers=headers, tablefmt="pretty"))
            
            # Load old node list
            with open(file_path+'node-archive.txt', 'r') as f:
                node_list = json.load(f)
            
            # Create the node list as a dictionary
            for line in parsed_data[1:]:
                try:
                    # if a node has been seen before, check if there's any new information to capture
                    if line[15] not in node_list[line[2]]['Times Heard'] and line[15] != "N/A":
                        node_list[line[2]]['Times Heard'].append(line[15])
                        print('Last heard updated for', line[1], line[3])
                    if node_list[line[2]]['Short Name'] != line[3]:
                        node_list[line[2]]['Short Name'] = line[3]
                        print('Short name updated for', line[1], line[3])
                    if node_list[line[2]]['Long Name'] != line[1] and line[1] != node_list[line[2]]['AKA']:
                        node_list[line[2]]['Long Name'] = line[1] 
                        print('Long name updated for', line[1], line[3])
                    if node_list[line[2]]['Hardware'] != line[5]:
                        node_list[line[2]]['Hardware'] = line[5]
                        print('Hardware updated for', line[1], line[3])
                    if node_list[line[2]]['Latitude'] != line[6]:
                        node_list[line[2]]['Latitude'] = line[6]
                        print('Latitude updated for', line[1], line[3])
                    if node_list[line[2]]['Longitude'] != line[7]:
                        node_list[line[2]]['Longitude'] = line[7]
                        print('Longitude updated for', line[1], line[3])
                    if node_list[line[2]]['Altitude'] != line[8]:
                        node_list[line[2]]['Altitude'] = line[8]
                        print('Altitude updated for', line[1], line[3])
                    if node_list[line[2]]['Hops Away'] != line[13]:
                        node_list[line[2]]['Hops Away'] = line[13]
                        print('Hops away updated for', line[1], line[3])
                    if node_list[line[2]]['Channel'] != line[14]:
                        node_list[line[2]]['Channel'] = line[14]
                        print('Channel updated for', line[1], line[3])
                except KeyError:
                    # if a node is brand new and isn't in the database already, add the new info
                    print('new node', line[2])
                    node_list[line[2]] = {
                                            'ID': line[2], 
                                            'Short Name': line[3], 
                                            'Long Name': line[1], 
                                            'AKA': line[4],
                                            'Hardware': line[5],
                                            'Latitude': line[6],
                                            'Longitude': line[7],
                                            'Altitude': line[8],
                                            'Channel Util': line[10],
                                            'Tx Air Util': line[11],
                                            'Hops Away': line[13],
                                            'Channel': line[14],
                                            'Times Heard':[]
                                            }
                    if line[15] != "N/A":
                        node_list[line[2]]['Times Heard'].append(line[15])
                    else:
                        # sometime the time is n/a. not sure why this is, but you can't let it add "n/a" to the list
                        # or things will be messed up down the line. i used to add it to the database but with no time
                        # but this means it won't show up on the board. I opted to add the current date and time.
                        # this isn't super accurate, if you update the database every X mins this time could be off by
                        # X or more. but whatever.
                        node_list[line[2]]['Times Heard'].append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    print('New node', line[3], 'added')
            
            # Pretty print the node list in JSON format
            #print(json.dumps(node_list, indent=4))
            
            # Save the JSON output to a file 'node-archive.txt'
            with open(file_path +'node-archive.txt', 'w') as f:
                json.dump(node_list, f, indent=4)
            print("Node list saved to 'node-archive.txt'.")
            
        else:
            print(f"Error: Command failed with return code {result.returncode}")
            print(result.stderr)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_meshtastic_nodes()
