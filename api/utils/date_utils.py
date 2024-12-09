from datetime import datetime, timedelta


def get_current_date(date_format="%d/%m/%Y") -> str:
    """Returns current date."""

    return datetime.now().strftime(date_format)


def get_date_format(date_string: str, date_formats=[]):
    """Returns date format of a given string."""

    if not date_formats:
        date_formats = [
            "%d/%m",
            "%d/%m/%Y",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%m/%d/%Y %H:%M:%S",
            "%m/%d/%Y %H:%M",
            "%m/%d/%Y",
        ]

    for date_format in date_formats:
        try:

            datetime.strptime(date_string, date_format)
            return date_format

        except ValueError:
            pass


def parse_date(date_string: str, target_format: str = "%d/%m/%Y"):
    """Parses a date to a specified format."""

    date_format = get_date_format(date_string)

    print(date_format)
    if date_format:
        formatted_date = datetime.strptime(date_string, date_format)
        return formatted_date.strftime(target_format)
    else:
        raise ValueError("Not a valid date.")


def get_time_format(time_string: str, time_formats: list = []):
    """Returns time format of a given string."""

    if not time_formats:
        time_formats = ["%H:%M:%S", "%H:%M"]

    for format in time_formats:
        try:
            datetime.strptime(time_string, format)
            return format
        except ValueError:
            pass


def parse_time(
    time_string: str, time_format: str = "%H:%M:%S", time_formats: list = []
):
    """Parses a time to a specified format."""

    if not time_formats:
        time_formats = ["%H:%M:%S", "%H:%M"]

    try:
        valid_format = get_time_format(time_string)

        if valid_format and time_format in time_formats:
            date_object = datetime.strptime(time_string, valid_format)
            return date_object.strftime(time_format)

    except ValueError as e:
        print(e)


def parse_time_range(time_range: str):
    """Returns start and end time given a time range."""

    start_time, end_time = time_range.split(" - ")

    if not get_time_format(start_time) or not get_time_format(end_time):
        raise ValueError("Not a valid time range.")

    return start_time, end_time
