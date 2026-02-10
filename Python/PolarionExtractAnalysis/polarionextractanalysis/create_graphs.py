from typing import List

import matplotlib.pyplot
import pandas
import plotly.graph_objects as go
from common import file_name_utils
from logger import logger_config

from polarionextractanalysis import polarion_data_model

EXCEL_FILE_EXTENSION = ".xlsx"


def create_baregraph_work_item_per_user(output_directory_path: str, users_library: polarion_data_model.PolarionUsersLibrary) -> None:

    with logger_config.stopwatch_with_label("create_baregraph_work_item_per_user"):
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


def create_baregraph_work_item_number_by_status_by_type(output_directory_path: str, polarion_library: polarion_data_model.PolarionLibrary) -> None:

    for work_item_type in polarion_library.work_item_library.all_work_items_by_type.keys():
        with logger_config.stopwatch_with_label(f"create_baregraph_work_item_number_by_status_by_type, type {work_item_type.name}"):
            work_items = polarion_library.work_item_library.all_work_items_by_type[work_item_type]
            found_status = set([work_item.attributes.status for work_item in work_items])

            df = pandas.DataFrame(
                [
                    {
                        "Status": status.name,
                        f"Number of work items {work_item_type}": len([work_item for work_item in work_items if work_item.attributes.status == status]),
                    }
                    for status in found_status
                ]
            )
            df.plot.bar(use_index=True, x="Status", y=f"Number of work items {work_item_type}", rot=90, color="#9a95d1")
            common_output_label = f"baregraph_work_item_{work_item_type.name}_per_status"
            matplotlib.pyplot.savefig(f"{output_directory_path}/{common_output_label}{file_name_utils.get_file_suffix_with_current_datetime()}.png")

            # Create HTML page with Plotly bar graph
            num_bars = len(df)
            figure_width = max(800, num_bars * 100)
            fig = go.Figure(data=[go.Bar(x=df["Status"], y=df[f"Number of work items {work_item_type}"], marker=dict(color="#9a95d1"), width=0.1)])
            fig.update_layout(title=f"{work_item_type} per status", xaxis_title="Status", yaxis_title="Number of work items", hovermode="x unified", width=figure_width)
            fig.write_html(f"{output_directory_path}/{common_output_label}{file_name_utils.get_file_suffix_with_current_datetime()}.html")


def create_baregraph_work_item_number_cumulative_by_status(output_directory_path: str, polarion_library: polarion_data_model.PolarionLibrary) -> None:

    with logger_config.stopwatch_with_label("create_baregraph_work_item_number_cumulative_by_status"):
        # Collect data for all work item types and statuses
        data_dict = {}
        all_statuses = set()
        
        for work_item_type in polarion_library.work_item_library.all_work_items_by_type.keys():
            work_items = polarion_library.work_item_library.all_work_items_by_type[work_item_type]
            found_status = set([work_item.attributes.status for work_item in work_items])
            all_statuses.update(found_status)
            
            data_dict[work_item_type.name] = {}
            for status in found_status:
                count = len([work_item for work_item in work_items if work_item.attributes.status == status])
                data_dict[work_item_type.name][status.name] = count
        
        # Fill missing status values with 0
        for work_item_type in data_dict.keys():
            for status in all_statuses:
                if status.name not in data_dict[work_item_type]:
                    data_dict[work_item_type][status.name] = 0
        
        # Create stacked bar chart with Plotly
        fig = go.Figure()
        
        for status in sorted([s.name for s in all_statuses]):
            values = [data_dict[wit].get(status, 0) for wit in sorted(data_dict.keys())]
            fig.add_trace(go.Bar(
                x=sorted(data_dict.keys()),
                y=values,
                name=status
            ))
        
        figure_width = max(800, len(data_dict) * 150)
        fig.update_layout(
            title="Work Items per Type by Status (Stacked)",
            xaxis_title="Work Item Type",
            yaxis_title="Number of work items",
            barmode="stack",
            hovermode="x unified",
            width=figure_width
        )
        
        common_output_label = "baregraph_work_item_cumulative_per_status"
        fig.write_html(f"{output_directory_path}/{common_output_label}{file_name_utils.get_file_suffix_with_current_datetime()}.html")
