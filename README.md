This code runs on a Raspberry Pi in the Faire office. It records video into a circular buffer, and when the Clip button is finished it saves the **past** 20 seconds of footage. 

To push updates, simply merge code to main and the Raspberry Pi will pull it when it is next rebooted.

## Guide:
On the actual bot, the flashing red light indicates that it’s recording. The green light should always be on, if it’s not there’s an issue with the script.
When the light is flashing, the bot is always recording and pushing the red button will save the PAST 20 seconds of footage.
When you’re done, hold the clip button down until the red light flashes fast a bunch of times. It should then be off (green light on but no flashing red light).
To wake it up, just press the clip button. It should start flashing red again.
## Commands:
Use @Highlight Bot list to list out all the saved clips in the bot. It'll list them 0-indexed and include when they were saved.
Use @Highlight Bot collect  to have the bot send clips. You can also include a list of indices to collect, that will make the bot only collect those indices. If no indices are included, all clips will be sent
Eg. @Highlight Bot collect 0 1 4  would collect the 0th, 1st, and 4th highlights.
The bot will delete the clips from local storage when you collect them!
You can also say @Highlight Bot delete  with or without indices to delete clips without sending.
