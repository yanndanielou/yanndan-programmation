# -*-coding:Utf-8 -*
""" Date time formats """
def format_duration_to_string(duration_in_seconds_as_float: float) -> str:
    """ Formatter for duration """
    milliseconds = int(duration_in_seconds_as_float*1000) % 1000

    duration_in_seconds_as_int = int(duration_in_seconds_as_float)

    hours, remainder = divmod(duration_in_seconds_as_int, 3600)
    minutes, seconds = divmod(remainder, 60)

    result = '{:02}:{:02}:{:02}.{:03}'.format(
        int(hours),
        int(minutes),
        int(seconds),
        int(milliseconds))

    return result
