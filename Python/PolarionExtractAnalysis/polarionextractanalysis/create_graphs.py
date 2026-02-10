from typing import List

import matplotlib.pyplot
import pandas
import plotly.graph_objects as go
from common import file_name_utils
from logger import logger_config

from polarionextractanalysis import polarion_data_model

EXCEL_FILE_EXTENSION = ".xlsx"


def create_baregraph_work_item_per_user(output_directory_path: str, users_library: polarion_data_model.PolarionUsersLibrary) -> None:

    df = pandas.DataFrame(
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
    matplotlib.pyplot.savefig(f"{output_directory_path}/baregraph_work_item_per_user{file_name_utils.get_file_suffix_with_current_datetime()}.png")

    # Create HTML page with Plotly bar graph
    fig = go.Figure(data=[go.Bar(x=df["Full name"], y=df["Number of work items"], marker=dict(color="#9a95d1"))])
    fig.update_layout(title="Work Items per User", xaxis_title="Full name", yaxis_title="Number of work items", hovermode="x unified")
    fig.write_html(f"{output_directory_path}/baregraph_work_item_per_user{file_name_utils.get_file_suffix_with_current_datetime()}.html")
