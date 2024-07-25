import threading
from slack_sdk.errors import SlackApiError
from flask import Response
from get_sorted_videos import get_sorted_videos
from upload_with_slack import upload_videos_sequentially
import os

def send_all_clips(client, event,reply_thread):
    message = event.get("message")
    channel = event.get("channel")
    ts = event.get("ts")
    clip_count = len(get_sorted_videos())
    if clip_count==0:
        reply_thread("No clips saved.")
        return Response(status=200)
    try:
        reply_thread(f"Sending {clip_count} clips!")
        threading.Thread(target=upload_videos_sequentially,args=(client,channel,ts)).start()
        return Response(status=200)
    except SlackApiError as e:
        print(f"Error posting message: {e.response['error']}")
        return Response(status=500)