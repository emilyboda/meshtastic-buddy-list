# ePaper Buddy List for Meshtastic

Here you will find the code for the ePaper Buddy List for Meshtastic. Much kudos to [Steve over at Iffy Books](https://github.com/iffybooks/meshtastic-buddy-list/tree/main) who did something very similar and gave me the idea to display this on an ePaper screen.

Read my full write-up on how this works [on my website](https://boda.codes/post/meshtastic-buddy-list).

Clone the files to your Raspberry Pi. My virtual environment was called `buddylist` and I made a second folder in my home directory called `buddylist-files` where my files live. I decided to run them using crontab. 

Here's my commands, which also log any issues to a log file:
```
*/3 * * * * /bin/bash -c "source /home/pi/buddylist/bin/activate && /home/pi/buddylist/bin/python3 /home/pi/buddylist-files/update-node-list.py >> /home/pi/buddylist-files/update-node-list.log 2>&1"
*/3 * * * * /bin/bash -c "source /home/pi/buddylist/bin/activate && sleep 60; /home/pi/buddylist/bin/python3 /home/pi/buddylist-files/update-buddy-list.py >> /home/pi/buddylist-files/update-buddy-list.log 2>&1"
2 23 */3 * * /bin/bash -c "source /home/pi/buddylist/bin/activate && sleep 60; /home/pi/buddylist/bin/python3 /home/pi/buddylist-files/node-list-cleanup.py >> /home/pi/buddylist-files/node-list-cleanup.log 2>&1"
```
