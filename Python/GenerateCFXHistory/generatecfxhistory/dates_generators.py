import datetime
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import List

from dateutil import relativedelta
from logger import logger_config


def get_today_naive() -> datetime.datetime:
    today_naive = datetime.datetime.now().replace(tzinfo=None)
    return today_naive


def get_tomorrow_naive() -> datetime.datetime:
    tomorrow_naive = (datetime.datetime.now() + timedelta(days=1)).replace(tzinfo=None)
    return tomorrow_naive


class DatesGenerator(ABC):
    def __init__(self) -> None:
        pass

    def get_dates_since(self, start_date: datetime.datetime) -> List[datetime.datetime]:
        all_dates: List[datetime.datetime] = self._compute_dates_since_until_today(start_date=start_date)
        # Add today if not exist
        today_naive = get_today_naive()
        if today_naive not in all_dates:
            all_dates.append(today_naive)

        # Add tomorrow  if not exist
        tomorrow_naive = get_tomorrow_naive()
        if tomorrow_naive not in all_dates:
            all_dates.append(tomorrow_naive)

        logger_config.print_and_log_info(f"Number of dates since:{start_date}: {len(all_dates)}")
        return all_dates

    @abstractmethod
    def _compute_dates_since_until_today(self, start_date: datetime.datetime) -> List[datetime.datetime]:
        return []


class SpecificForTestsDatesGenerator(DatesGenerator):
    def __init__(self, all_dates_to_generate: List[datetime.datetime]) -> None:
        super().__init__()
        self._all_dates_to_generate: List[datetime.datetime] = all_dates_to_generate

    def get_dates_since(self, start_date: datetime.datetime) -> List[datetime.datetime]:
        return self._all_dates_to_generate

    def _compute_dates_since_until_today(self, start_date: datetime.datetime) -> List[datetime.datetime]:
        return []


class ConstantIntervalDatesGenerator(DatesGenerator):
    def __init__(self, time_delta: relativedelta.relativedelta) -> None:
        super().__init__()
        self._time_delta = time_delta

    def _compute_dates_since_until_today(self, start_date: datetime.datetime) -> List[datetime.datetime]:
        dates = []

        today_naive = get_today_naive()

        # Ensure 'current_date' is naive datetime.datetime
        current_date_iter = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        while current_date_iter <= today_naive:
            dates.append(current_date_iter)
            next_date = current_date_iter + self._time_delta
            assert next_date != current_date_iter
            current_date_iter = next_date

        return dates


class DecreasingIntervalDatesGenerator(DatesGenerator):
    def _compute_dates_since_until_today(self, start_date: datetime.datetime) -> List[datetime.datetime]:

        # Ensure 'beginning_of_next_month' is naive datetime.datetime
        today_naive = get_today_naive()

        dates = []

        # Ensure 'current_date' is naive datetime.datetime
        current_date_iter = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)

        while current_date_iter <= today_naive:
            dates.append(current_date_iter)

            current_date_delta_with_now = datetime.datetime.now() - current_date_iter
            days_diff = current_date_delta_with_now.days

            # Compare using days to determine the time delta
            if days_diff > 365 * 3:
                time_delta = relativedelta.relativedelta(months=3)

            elif days_diff > 365 * 2:
                time_delta = relativedelta.relativedelta(months=2)

            elif days_diff > 365:
                time_delta = relativedelta.relativedelta(months=1)

            elif days_diff > 180:
                time_delta = relativedelta.relativedelta(weeks=2)

            elif days_diff > 30:
                time_delta = relativedelta.relativedelta(weeks=1)

            elif days_diff > 15:
                time_delta = relativedelta.relativedelta(days=3)

            elif days_diff > 7:
                time_delta = relativedelta.relativedelta(days=2)

            else:
                time_delta = relativedelta.relativedelta(days=1)

            current_date_iter += time_delta

        return dates
