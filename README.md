# ePaper Buddy List for Meshtastic

![Buddy list picture](/buddy_list_mounted.jpg)

Here you will find the code for the ePaper Buddy List for Meshtastic. Much kudos to [Steve over at Iffy Books](https://github.com/iffybooks/meshtastic-buddy-list/tree/main) who did something very similar and gave me the idea to display this on an ePaper screen.

Read my full write-up on how this works [on my website](https://boda.codes/post/meshtastic-buddy-list).

Clone the files to your Raspberry Pi. My virtual environment was called `buddylist` and I made a second folder in my home directory called `buddylist-files` where my files live.

You will also need to following the [instructions from Waveshare's Wiki](https://www.waveshare.com/wiki/2.7inch_e-Paper_HAT_Manual#Working_With_Raspberry_Pi) to install the required packages. I copied the [`waveshare_epd`](https://github.com/waveshareteam/e-Paper/tree/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd) directory that is downloaded as part of the examples to the same directory my scripts, so that's how the file paths are structured in `update-buddy-list.py`.

I've also uploaded two random font files that I had from a previous project. Not sure where they came from, but I put those in the `waveshare_epd` directory as well.

Here's my crontab commands, which also log any issues to a log file:
```
*/3 * * * * /bin/bash -c "source /home/pi/buddylist/bin/activate && /home/pi/buddylist/bin/python3 /home/pi/buddylist-files/update-node-list.py >> /home/pi/buddylist-files/update-node-list.log 2>&1"
*/3 * * * * /bin/bash -c "source /home/pi/buddylist/bin/activate && sleep 60; /home/pi/buddylist/bin/python3 /home/pi/buddylist-files/update-buddy-list.py >> /home/pi/buddylist-files/update-buddy-list.log 2>&1"
2 23 */3 * * /bin/bash -c "source /home/pi/buddylist/bin/activate && sleep 60; /home/pi/buddylist/bin/python3 /home/pi/buddylist-files/node-list-cleanup.py >> /home/pi/buddylist-files/node-list-cleanup.log 2>&1"
```
