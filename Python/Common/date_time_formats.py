# -*-coding:Utf-8 -*
""" Date time formats """
def format_duration_to_string(duration_in_seconds_as_float: float) -> str:
    """ Formatter for duration """
    milliseconds = int(duration_in_seconds_as_float*1000) % 1000

    duration_in_seconds_as_int = int(duration_in_seconds_as_float)

    hours, remainder = divmod(duration_in_seconds_as_int, 3600)
    minutes, seconds = divmod(remainder, 60)

    result = f'{int(hours):02}:{int(minutes):02}:{int(seconds):02}.{int(milliseconds):03}'

    return result
