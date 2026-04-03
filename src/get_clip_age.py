from datetime import datetime

from clip_db import get_clip_by_filename


def get_clip_age(file_name):
    clip = get_clip_by_filename(file_name)
    if clip is None:
        return "unknown"

    recorded_time = clip["created_at"]
    time_difference = datetime.now() - recorded_time

    days = time_difference.days
    hours = time_difference.seconds // 3600
    minutes = (time_difference.seconds // 60) % 60
    seconds = time_difference.seconds % 60

    message = ""

    if days:
        message += f"{days} day{days > 1 and 's' or ''}, "
    if hours:
        message += f"{hours} hour{hours > 1 and 's' or ''}, "
    if minutes:
        message += f"{minutes} minute{minutes > 1 and 's' or ''}, "
    message += f"{seconds} second{seconds > 1 and 's' or ''} ago"

    return message
