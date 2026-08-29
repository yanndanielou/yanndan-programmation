import datetime
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import List

from dateutil import relativedelta
from logger import logger_config


def get_now_naive() -> datetime.datetime:
    now_naive = datetime.datetime.now().replace(tzinfo=None)
    return now_naive


def get_tomorrow_naive() -> datetime.datetime:
    tomorrow_naive = (datetime.datetime.now() + timedelta(days=1)).replace(tzinfo=None)
    return tomorrow_naive


def get_day_after_tomorrow_naive() -> datetime.datetime:
    tomorrow_naive = (datetime.datetime.now() + timedelta(days=2)).replace(tzinfo=None)
    return tomorrow_naive


class DatesGenerator(ABC):
    def __init__(self) -> None:
        pass

    def get_dates_since(self, start_date: datetime.datetime) -> List[datetime.datetime]:
        all_dates: list[datetime.datetime] = self._compute_dates_since_until_now(start_date=start_date)
        # Add today if not exist
        now_naive = get_now_naive()
        if now_naive not in all_dates:
            all_dates.append(now_naive)

        # Add tomorrow  if not exist

        for additional_days_in_future_to_add in range(1, 5):
            additional_date_to_add = (datetime.datetime.now() + timedelta(days=additional_days_in_future_to_add)).replace(tzinfo=None)
            if additional_date_to_add not in all_dates:
                all_dates.append(additional_date_to_add)

        logger_config.print_and_log_info(f"Number of dates since:{start_date}: {len(all_dates)}")
        return all_dates

    @abstractmethod
    def _compute_dates_since_until_now(self, start_date: datetime.datetime) -> List[datetime.datetime]:
        return []


class SpecificForTestsDatesGenerator(DatesGenerator):
    def __init__(self, all_dates_to_generate: List[datetime.datetime]) -> None:
        super().__init__()
        self._all_dates_to_generate: List[datetime.datetime] = all_dates_to_generate

    def get_dates_since(self, start_date: datetime.datetime) -> List[datetime.datetime]:
        return self._all_dates_to_generate

    def _compute_dates_since_until_now(self, start_date: datetime.datetime) -> List[datetime.datetime]:
        return []


class ConstantIntervalDatesGenerator(DatesGenerator):
    def __init__(self, time_delta: relativedelta.relativedelta) -> None:
        super().__init__()
        self._time_delta = time_delta

    def _compute_dates_since_until_now(self, start_date: datetime.datetime) -> List[datetime.datetime]:
        dates = []

        now_naive = get_now_naive()

        # Ensure 'current_date' is naive datetime.datetime
        current_date_iter = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        while current_date_iter <= now_naive:
            dates.append(current_date_iter)
            next_date = current_date_iter + self._time_delta
            assert next_date != current_date_iter
            current_date_iter = next_date

        return dates


class DecreasingIntervalDatesGenerator(DatesGenerator):
    def _compute_dates_since_until_now(self, start_date: datetime.datetime) -> List[datetime.datetime]:

        # Ensure 'beginning_of_next_month' is naive datetime.datetime
        now_naive = get_now_naive()

        dates = []

        # Ensure 'current_date' is naive datetime.datetime
        current_date_iter = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)

        while current_date_iter <= now_naive:
            dates.append(current_date_iter)

            current_date_delta_with_now = datetime.datetime.now() - current_date_iter
            days_diff = current_date_delta_with_now.days

            # Compare using days to determine the time delta
            if days_diff > 365 * 10:
                time_delta = relativedelta.relativedelta(months=4)

            elif days_diff > 365 * 7:
                time_delta = relativedelta.relativedelta(months=3)

            elif days_diff > 365 * 5:
                time_delta = relativedelta.relativedelta(months=2)

            elif days_diff > 365:
                time_delta = relativedelta.relativedelta(months=1)

            elif days_diff > 180:
                time_delta = relativedelta.relativedelta(weeks=2)

            elif days_diff > 100:
                time_delta = relativedelta.relativedelta(weeks=1)

            elif days_diff > 80:
                time_delta = relativedelta.relativedelta(days=6)

            elif days_diff > 60:
                time_delta = relativedelta.relativedelta(days=5)

            elif days_diff > 40:
                time_delta = relativedelta.relativedelta(days=3)

            elif days_diff > 20:
                time_delta = relativedelta.relativedelta(days=2)

            elif days_diff > 3:
                time_delta = relativedelta.relativedelta(days=1)

            elif days_diff > 2:
                time_delta = relativedelta.relativedelta(hours=12)

            elif days_diff > 1:
                time_delta = relativedelta.relativedelta(hours=6)

            else:
                time_delta = relativedelta.relativedelta(hours=2)

            current_date_iter += time_delta

        return dates
