from django.utils import timezone

def common_user_str(user):
    if not user:
        return ''
    return user.full_name if user.full_name else user.email

def common_datetime_str(datetime):
    if not datetime:
        return ''
    return datetime.strftime("%Y.%m.%d %H:%M")

def common_date_str(datetime):
    if not datetime:
        return ''
    return datetime.strftime("%Y.%m.%d")

def file_name_datetime_str():
    dt = timezone.now()
    return f'{dt.year}-{dt.month}-{dt.day}-{dt.hour}-{dt.minute}-{dt.second}'
