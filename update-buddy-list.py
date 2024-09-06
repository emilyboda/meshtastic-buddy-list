#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os

import logging
from waveshare_epd import epd2in7
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import json
from datetime import datetime, timedelta

logging.basicConfig(level=logging.WARNING)
always_update = 1 #set to zero for normal operation, 1 for development to make it update every time
font_size = 13
max_list_len = 14
char_limit = 20
node_block_list = []
    # the node block list lets you omit certain nodes from you list. I put all my own nodes here.
file_path = "/home/pi/buddylist-files/"

# Define time ranges
now = datetime.now()
active_ago = now - timedelta(minutes=17) 
twenty_four_hours_ago = now - timedelta(hours=24)
one_week_ago = now - timedelta(weeks=1)

# Lists to store nodes based on last seen time
last_active = []
last_24_hours = []
last_1_week = []

def categorize_nodes(node_list):
    for node_id, node_data in node_list.items():
        # Extract the most recent time and the first time the node was heard
        times_heard = node_data.get('Times Heard', [])
        
        if not times_heard:
            continue  # Skip if no Times Heard data
        
        # Convert the most recent and first "Times Heard" entries to datetime objects
        last_heard_str = times_heard[-1]
        last_heard_time = datetime.strptime(last_heard_str, "%Y-%m-%d %H:%M:%S")
        
        first_heard_str = times_heard[0]
        first_heard_time = datetime.strptime(first_heard_str, "%Y-%m-%d %H:%M:%S")
        
        # If the node name is in the block list, don't add it to any of these lists
        if node_data['Long Name'] in node_block_list:
            continue
        
        # Check if the device is new (first seen within the last week)
        if first_heard_time > twenty_four_hours_ago:
            # If the node was first seen within the last 24 hours, add two asterisks
            long_name = f"**{node_data['Long Name']}"
        elif first_heard_time > one_week_ago:
            # If the node was first seen within the last week but more than 24 hours ago, add one asterisk
            long_name = f"*{node_data['Long Name']}"
        else:
            # If the node is older than one week, no asterisk
            long_name = node_data['Long Name']
            
        # Check which time range the last heard time falls into
        if last_heard_time > active_ago:
            last_active.append(long_name)
        elif active_ago >= last_heard_time > twenty_four_hours_ago:
            last_24_hours.append(long_name)
        elif twenty_four_hours_ago >= last_heard_time > one_week_ago:
            last_1_week.append(long_name)

    last_active.sort()
    last_24_hours.sort()
    last_1_week.sort()

def load_full_list_from_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            return [line.strip() for line in file.readlines()]
    return []

def save_full_list_to_file(filepath, full_list):
    with open(filepath, 'w') as file:
        for item in full_list:
            file.write(item + "\n")

def main():
    try:
        # Load the node-archive.txt file
        with open(file_path+'node-archive.txt', 'r') as file:
            node_list = json.load(file)
        
        # Categorize the nodes based on their last heard time
        categorize_nodes(node_list)

        # These are the titles for each section
        active_name = "ACTIVE"
        hours24_name = "TODAY"
        week1_name = "THIS WEEK"
        
        # This creates one list that is all of the entries
        full_list = []
        if last_active != []:
            full_list.append(active_name)
            for entry in last_active:
                full_list.append(entry[0:char_limit])
        if last_24_hours != []:
            if full_list != []:
                full_list.append("")
            full_list.append(hours24_name)
            for entry in last_24_hours:
                full_list.append(entry[0:char_limit])
        if last_1_week != []:
            if full_list != []:
                full_list.append("")
            full_list.append(week1_name)
            for entry in last_1_week:
                full_list.append(entry[0:char_limit])
        
        saved_full_list = load_full_list_from_file(file_path+'full_list.txt')
            # save it so you don't have to update next time if nothing has changed.
        
        if saved_full_list != full_list or always_update == 1:
            print(datetime.now(), 'different list than before, updating')
            logging.info("epd2in7 Demo")   
            epd = epd2in7.EPD()
            
            '''2Gray(Black and white) display'''
            logging.info("init and Clear")
            epd.init()
            epd.Clear(0xFF)
            
            
            my_font = ImageFont.truetype(file_path+'waveshare_epd/NotoSansUI-Regular.ttf', font_size)
            my_font_bold = ImageFont.truetype(file_path+'waveshare_epd/NotoSansUI-Bold.ttf', font_size)

            Himage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
            draw = ImageDraw.Draw(Himage)

            text_bbox = my_font.getbbox('Active')
            text_size = (text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1])

            spacing = 2
            
            # yes there is probably a way better way of doing this but I did this project piece by piece and didn't
            # want to rewrite the old stuff so here we are ¯\_(ツ)_/¯
            
            if len(full_list) > max_list_len:
                # if the list will be two columns
                if full_list[max_list_len-1] == hours24_name or full_list[max_list_len-1] == week1_name:
                    # if a heading falls on the last entry in a column, shorten the first column by one and put the rest on the second column
                    starting_y = 0
                    for entry in full_list[0:max_list_len-1]:
                        if entry == hours24_name or entry == week1_name or entry == active_name:
                            draw.text((4, starting_y), entry, font = my_font_bold, fill=0)
                            starting_y = starting_y + text_size[1]+spacing
                        else:
                            draw.text((4, starting_y), entry, font = my_font, fill=0)
                            starting_y = starting_y + text_size[1]+spacing

                    starting_y = 0
                    for entry in full_list[max_list_len-1:]:
                        if entry == hours24_name or entry == week1_name or entry == active_name:
                            draw.text((132, starting_y), entry, font = my_font_bold, fill=0)
                            starting_y = starting_y + text_size[1]+spacing
                        else:
                            draw.text((132, starting_y), entry, font = my_font, fill=0)
                            starting_y = starting_y + text_size[1]+spacing
                            
                elif full_list[max_list_len] == "":
                    # if the first entry on the second column is a blank space, eliminate the space by starting the second column one entry later
                    starting_y = 0
                    for entry in full_list[0:max_list_len]:
                        if entry == hours24_name or entry == week1_name or entry == active_name:
                            draw.text((4, starting_y), entry, font = my_font_bold, fill=0)
                            starting_y = starting_y + text_size[1]+spacing
                        else:
                            draw.text((4, starting_y), entry, font = my_font, fill=0)
                            starting_y = starting_y + text_size[1]+spacing
                                            
                    starting_y = 0
                    for entry in full_list[max_list_len+1:]:
                        if entry == hours24_name or entry == week1_name or entry == active_name:
                            draw.text((132, starting_y), entry, font = my_font_bold, fill=0)
                            starting_y = starting_y + text_size[1]+spacing
                        else:
                            draw.text((132, starting_y), entry, font = my_font, fill=0)
                            starting_y = starting_y + text_size[1]+spacing
                else:
                    # if there are no weird circumstances, do this
                    starting_y = 0
                    for entry in full_list[0:max_list_len]:
                        if entry == hours24_name or entry == week1_name or entry == active_name:
                            draw.text((4, starting_y), entry, font = my_font_bold, fill=0)
                            starting_y = starting_y + text_size[1]+spacing
                        else:
                            draw.text((4, starting_y), entry, font = my_font, fill=0)
                            starting_y = starting_y + text_size[1]+spacing
                    
                    starting_y = 0
                    for entry in full_list[max_list_len:]:
                        if entry == hours24_name or entry == week1_name or entry == active_name:
                            draw.text((132, starting_y), entry, font = my_font_bold, fill=0)
                            starting_y = starting_y + text_size[1]+spacing
                        else:
                            draw.text((132, starting_y), entry, font = my_font, fill=0)
                            starting_y = starting_y + text_size[1]+spacing
            else:
                # if the list is only one column
                print('not greater than', max_list_len -1)
                starting_y = 0
                for entry in full_list:
                    if entry == hours24_name or entry == week1_name or entry == active_name:
                        draw.text((4, starting_y), entry, font = my_font_bold, fill=0)
                        starting_y = starting_y + text_size[1]+spacing
                    else:
                        draw.text((4, starting_y), entry, font = my_font, fill=0)
                        starting_y = starting_y + text_size[1]+spacing
                    
            save_full_list_to_file(file_path+'full_list.txt', full_list)
                    
            epd.display(epd.getbuffer(Himage))
            time.sleep(2)

            logging.info("Goto Sleep...")
            epd.sleep()
        else:
            print(datetime.now(), 'same list as before, did not update')
        
    
    except FileNotFoundError:
        print("Error: The file 'node-archive.txt' was not found.")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from 'node-archive.txt'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()