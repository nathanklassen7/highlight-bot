import os
from datetime import datetime

from flask import Response

from consts import CLIP_DIRECTORY
from get_sorted_videos import get_sorted_videos

def list_videos(reply_thread):
    try:
        # List all files in the directory
        files = get_sorted_videos()
        
        videos_with_age = []

        message = ''
        
        for file_name in files:
            # Check if the file has a valid video format
            if file_name.endswith('.mp4'):
                try:
                    # Extract the timestamp part from the filename
                    timestamp_str = file_name.split('.')[0]
                    
                    # Parse the timestamp into a datetime object
                    recorded_time = datetime.strptime(timestamp_str, '%Y-%m-%d-%H:%M:%S')
                    
                    # Calculate the time difference from now
                    current_time = datetime.now()
                    time_difference = current_time - recorded_time
                    
                    # Add the file and the time difference to the list
                    videos_with_age.append((file_name, time_difference))
                except ValueError:
                    print(f"Filename '{file_name}' does not match the expected format.")
        
        # Print the results
        for index, (video, age) in enumerate(videos_with_age):
            message += f"Highlight {index} - Recorded "
            days = age.days
            hours = age.seconds//3600 
            minutes = (age.seconds//60)%60
            if days:
                message += f"{days} days, "
            if hours:
                message += f"{hours} hours, "
            if hours or days:
                message += "and "
            if minutes:
                message += f"{minutes} minutes ago"
        print(message)
        reply_thread(message)
        return Response(status=200)
    except FileNotFoundError:
        print(f"The directory does not exist.")
        return Response(status=500)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return Response(status=500)
