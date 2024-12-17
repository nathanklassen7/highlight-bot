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

def get_time_difference(file_name1, file_name2):
    timestamp_str1 = file_name1.split('.')[0]
    timestamp_str2 = file_name2.split('.')[0]
    recorded_time1 = datetime.strptime(timestamp_str1, '%Y-%m-%d-%H:%M:%S')
    recorded_time2 = datetime.strptime(timestamp_str2, '%Y-%m-%d-%H:%M:%S')
    time_difference = recorded_time1 - recorded_time2
    return time_difference