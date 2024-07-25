from datetime import datetime


def get_clip_age(file_name):
    # Extract the timestamp part from the filename
    timestamp_str = file_name.split('.')[0]
    
    # Parse the timestamp into a datetime object
    recorded_time = datetime.strptime(timestamp_str, '%Y-%m-%d-%H:%M:%S')
    
    # Calculate the time difference from now
    current_time = datetime.now()
    time_difference = current_time - recorded_time

    days = time_difference.days
    hours = time_difference.seconds//3600 
    minutes = (time_difference.seconds//60)%60
    seconds = time_difference.seconds%60
    
    message = ""
    
    if days:
        message += f"{days} days, "
    if hours:
        message += f"{hours} hours, "
    if minutes:
        message += f"{minutes} minutes, "
    message += f"{seconds} seconds ago"
    
    return message