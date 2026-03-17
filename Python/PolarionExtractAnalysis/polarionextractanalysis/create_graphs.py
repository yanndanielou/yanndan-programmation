from typing import Dict, Set

import matplotlib.pyplot
import pandas
import plotly.graph_objects as go
from common import file_name_utils
from logger import logger_config

from polarionextractanalysis import polarion_data_model, constants

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
            fig.update_layout(title=f"{work_item_type.name} per status", xaxis_title="Status", yaxis_title="Number of work items", hovermode="x unified", width=figure_width)
            fig.write_html(f"{output_directory_path}/{common_output_label}{file_name_utils.get_file_suffix_with_current_datetime()}.html")


def create_baregraph_work_item_number_cumulative_by_status(output_directory_path: str, polarion_library: polarion_data_model.PolarionLibrary) -> None:

    with logger_config.stopwatch_with_label("create_baregraph_work_item_number_cumulative_by_status"):
        # Collect data for all work item types and statuses
        data_dict: Dict[str, Dict[str, int]] = {}
        all_statuses: Set[constants.PolarionStatus] = set()

        for work_item_type in polarion_library.work_item_library.all_work_items_by_type.keys():
            work_items = polarion_library.work_item_library.all_work_items_by_type[work_item_type]
            found_status = set([work_item.attributes.status for work_item in work_items])
            all_statuses.update(found_status)

            data_dict[work_item_type.name] = {}
            for status_enum in found_status:
                count = len([work_item for work_item in work_items if work_item.attributes.status == status_enum])
                data_dict[work_item_type.name][status_enum.name] = count

        # Create stacked bar chart with Plotly
        fig = go.Figure()

        for status_str in sorted([s.name for s in all_statuses]):
            present_keys = sorted([wit for wit in sorted(data_dict.keys()) if data_dict[wit].get(status_str, 0) > 0])
            values = [data_dict[wit].get(status_str, 0) for wit in present_keys]

            fig.add_trace(go.Bar(x=sorted(present_keys), y=values, name=status_str))

        figure_width = max(800, len(data_dict) * 150)
        fig.update_layout(title="Work Items per Type by Status (Stacked)", xaxis_title="Work Item Type", yaxis_title="Number of work items", barmode="stack", hovermode="x unified", width=figure_width)

        common_output_label = "baregraph_work_item_cumulative_per_status"
        fig.write_html(f"{output_directory_path}/{common_output_label}{file_name_utils.get_file_suffix_with_current_datetime()}.html")


def create_baregraph_work_item_number_by_company(output_directory_path: str, polarion_library: polarion_data_model.PolarionLibrary) -> None:

    with logger_config.stopwatch_with_label("create_baregraph_work_item_number_by_company"):
        # Build rows: one row per assignee -> company
        rows = []
        for work_item in polarion_library.work_item_library.all_work_items:
            for assignee in work_item.assignees:
                company = assignee.user_definition.company.full_name if assignee.user_definition and assignee.user_definition.company else "Unknown"
                rows.append({"Company": company, "count": 1})

        if not rows:
            return

        df = pandas.DataFrame(rows)
        # Use a pivot-style aggregation: sum of 'count' per Company
        pivot = df.pivot_table(index="Company", values="count", aggfunc="sum").reset_index().sort_values("count", ascending=False)

        # Save PNG using pandas/matplotlib
        pivot.plot.bar(use_index=True, x="Company", y="count", rot=90, color="#9a95d1")
        common_output_label = "baregraph_work_item_per_company"
        matplotlib.pyplot.savefig(f"{output_directory_path}/{common_output_label}{file_name_utils.get_file_suffix_with_current_datetime()}.png")

        # Create interactive HTML with Plotly
        num_bars = len(pivot)
        figure_width = max(800, num_bars * 150)
        fig = go.Figure(data=[go.Bar(x=pivot["Company"], y=pivot["count"], marker=dict(color="#9a95d1"))])
        fig.update_layout(title="Work Items per Company", xaxis_title="Company", yaxis_title="Number of work items", hovermode="x unified", width=figure_width)
        fig.write_html(f"{output_directory_path}/{common_output_label}{file_name_utils.get_file_suffix_with_current_datetime()}.html")


def create_baregraph_work_item_number_by_company_stacked_by_status(output_directory_path: str, polarion_library: polarion_data_model.PolarionLibrary) -> None:
    """
    For each work item type, create a stacked bar chart where each bar is a Company
    and segments are counts per Status (different colors per status). Saves PNG and HTML.
    """
    with logger_config.stopwatch_with_label("create_baregraph_work_item_number_by_company_stacked_by_status, all"):
        work_items = polarion_library.work_item_library.all_work_items

        # Build rows: one row per assignee -> company + status
        rows = []
        for work_item in work_items:
            status = work_item.attributes.status.name
            for assignee in work_item.assignees:
                company = assignee.user_definition.company.full_name if assignee.user_definition and assignee.user_definition.company else "Unknown"
                rows.append({"Company": company, "Status": status, "count": 1})

        assert rows

        df = pandas.DataFrame(rows)
        pivot = df.pivot_table(index="Company", columns="Status", values="count", aggfunc="sum")

        # Ensure consistent company order (descending total)
        pivot["_total"] = pivot.sum(axis=1)
        pivot = pivot.sort_values("_total", ascending=False).drop(columns=["_total"])

        # Save PNG using pandas (stacked)
        pivot.plot.bar(use_index=True, stacked=True, rot=90, colormap="tab20")
        common_output_label = "baregraph_work_item_all_per_company_stacked_status"
        matplotlib.pyplot.tight_layout()
        matplotlib.pyplot.savefig(f"{output_directory_path}/{common_output_label}{file_name_utils.get_file_suffix_with_current_datetime()}.png")
        matplotlib.pyplot.close()

        # Create interactive HTML with Plotly
        companies = pivot.index.tolist()
        statuses = pivot.columns.tolist()
        figure_width = max(800, len(companies) * 150)
        fig = go.Figure()
        for status in statuses:
            fig.add_trace(go.Bar(x=companies, y=pivot[status].tolist(), name=status))

        fig.update_layout(
            title="All - Work Items per Company by Status (Stacked)",
            xaxis_title="Company",
            yaxis_title="Number of work items",
            barmode="stack",
            hovermode="x unified",
            width=figure_width,
        )
        fig.write_html(f"{output_directory_path}/{common_output_label}{file_name_utils.get_file_suffix_with_current_datetime()}.html")


def create_baregraph_work_item_number_by_company_stacked_by_status_per_type(output_directory_path: str, polarion_library: polarion_data_model.PolarionLibrary) -> None:
    """
    For each work item type, create a stacked bar chart where each bar is a Company
    and segments are counts per Status (different colors per status). Saves PNG and HTML.
    """
    for work_item_type in polarion_library.work_item_library.all_work_items_by_type.keys():
        with logger_config.stopwatch_with_label(f"create_baregraph_work_item_number_by_company_stacked_by_status_per_type, type {work_item_type.name}"):
            work_items = polarion_library.work_item_library.all_work_items_by_type[work_item_type]

            # Build rows: one row per assignee -> company + status
            rows = []
            for work_item in work_items:
                status = work_item.attributes.status.name
                for assignee in work_item.assignees:
                    company = assignee.user_definition.company.full_name if assignee.user_definition and assignee.user_definition.company else "Unknown"
                    rows.append({"Company": company, "Status": status, "count": 1})

            if not rows:
                continue

            df = pandas.DataFrame(rows)
            pivot = df.pivot_table(index="Company", columns="Status", values="count", aggfunc="sum")

            # Ensure consistent company order (descending total)
            pivot["_total"] = pivot.sum(axis=1)
            pivot = pivot.sort_values("_total", ascending=False).drop(columns=["_total"])

            # Save PNG using pandas (stacked)
            pivot.plot.bar(use_index=True, stacked=True, rot=90, colormap="tab20")
            common_output_label = f"baregraph_work_item_{work_item_type.name}_per_company_stacked_status"
            matplotlib.pyplot.tight_layout()
            matplotlib.pyplot.savefig(f"{output_directory_path}/{common_output_label}{file_name_utils.get_file_suffix_with_current_datetime()}.png")
            matplotlib.pyplot.close()

            # Create interactive HTML with Plotly
            companies = pivot.index.tolist()
            statuses = pivot.columns.tolist()
            figure_width = max(800, len(companies) * 150)
            fig = go.Figure()
            for status in statuses:
                fig.add_trace(go.Bar(x=companies, y=pivot[status].tolist(), name=status))

            fig.update_layout(
                title=f"{work_item_type.name} - Work Items per Company by Status (Stacked)",
                xaxis_title="Company",
                yaxis_title="Number of work items",
                barmode="stack",
                hovermode="x unified",
                width=figure_width,
            )
            fig.write_html(f"{output_directory_path}/{common_output_label}{file_name_utils.get_file_suffix_with_current_datetime()}.html")


def create_baregraph_work_item_number_by_company_per_type(output_directory_path: str, polarion_library: polarion_data_model.PolarionLibrary) -> None:
    for work_item_type in polarion_library.work_item_library.all_work_items_by_type.keys():

        work_items = polarion_library.work_item_library.all_work_items_by_type[work_item_type]
        with logger_config.stopwatch_with_label(f"create_baregraph_work_item_number_by_company {work_item_type.name}, {len(work_items)} work items"):

            # Build rows: one row per assignee -> company
            rows = []
            for work_item in work_items:
                for assignee in work_item.assignees:
                    company = assignee.user_definition.company.full_name if assignee.user_definition and assignee.user_definition.company else "Unknown"
                    rows.append({"Company": company, "count": 1})

            if not rows:
                logger_config.print_and_log_warning(f"create_baregraph_work_item_number_by_company_per_type: no data for {work_item_type.name}")
                continue

            df = pandas.DataFrame(rows)
            # Use a pivot-style aggregation: sum of 'count' per Company
            pivot = df.pivot_table(index="Company", values="count", aggfunc="sum").reset_index().sort_values("count", ascending=False)

            # Save PNG using pandas/matplotlib
            pivot.plot.bar(use_index=True, x="Company", y="count", rot=90, color="#9a95d1")
            common_output_label = f"baregraph_work_item_per_company {work_item_type.name}"
            matplotlib.pyplot.savefig(f"{output_directory_path}/{common_output_label}{file_name_utils.get_file_suffix_with_current_datetime()}.png")

            # Create interactive HTML with Plotly
            num_bars = len(pivot)
            figure_width = max(800, num_bars * 150)
            fig = go.Figure(data=[go.Bar(x=pivot["Company"], y=pivot["count"], marker=dict(color="#9a95d1"))])
            fig.update_layout(title=f"{work_item_type.name} per Company", xaxis_title="Company", yaxis_title=f"Number of {work_item_type.name}", hovermode="x unified", width=figure_width)
            fig.write_html(f"{output_directory_path}/{common_output_label}{file_name_utils.get_file_suffix_with_current_datetime()}.html")
