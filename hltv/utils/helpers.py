from datetime import timedelta

days_by_period = {
    'year': timedelta(days = 365),
    'month': timedelta(days = 30)
}

def subtract_date_by_difference(date, diff):
    return (date.replace(day = 1) - diff).replace(day=date.day)