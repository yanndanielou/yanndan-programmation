from typing import List

import pandas as pd
from common import file_name_utils
from logger import logger_config
import matplotlib.pyplot
from polarionextractanalysis import polarion_data_model

EXCEL_FILE_EXTENSION = ".xlsx"


def create_baregraph_work_item_per_user(users_library: polarion_data_model.PolarionUsersLibrary) -> None:

    df = pd.DataFrame(
        [
            {
                "Full name": user.user_definition.full_name,
                "Number of work items": len(user.all_work_items_assigned),
            }
            for user in users_library.all_users
            if user.all_work_items_assigned
        ]
    )
    df.plot.bar(use_index=True, x="Full name", y="Number of work items", rot=90, color="#9a95d1")
    matplotlib.pyplot.show()
