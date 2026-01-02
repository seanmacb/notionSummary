import os
import requests
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
TASKS_DB = os.environ["TASKS_DB"]
PROJECTS_DB = os.environ["PROJECTS_DB"]
MY_USER = "U07QM549L4V"
NOTION_VERSION = "2022-06-28"
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}

skip_status = ["Done", "Canceled", "Backlog"]


# --------------------------
# Add a line to recall the benty-fields daily papers link
# --------------------------
def add_BentyFields():
    return "<https://www.benty-fields.com/daily_arXiv|Benty fields daily articles>"


def send_to_slack(text):
    """Send the weekly report to Slack via incoming webhook."""
    url = os.environ["SLACK_WEBHOOK_URL"]

    payload = {"text": text}

    resp = requests.post(url, json=payload)
    resp.raise_for_status()


# -------------------------------
# Query any Notion database (with pagination)
# -------------------------------
def query_db(db_id, filters=None):
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    data = {}
    if filters:
        data["filter"] = filters

    all_rows = []
    while True:
        resp = requests.post(url, headers=HEADERS, json=data)
        resp.raise_for_status()
        js = resp.json()

        all_rows.extend(js.get("results", []))

        if not js.get("has_more"):
            break

        data["start_cursor"] = js["next_cursor"]

    return all_rows


# -------------------------------
# Load project → status mapping
# -------------------------------


def get_projects():
    """Return mapping: project_id → {"name": ..., "status": ...}"""
    project_rows = query_db(PROJECTS_DB)
    mapping = {}

    for row in project_rows:
        proj_id = row["id"]
        props = row.get("properties", {})

        # ---- Project name ----
        title_prop = props.get("Project name", {})
        title_list = title_prop.get("title", [])
        name = title_list[0]["plain_text"] if title_list else "(Untitled project)"

        # ---- Project status ----
        status_prop = props.get("Status", {})
        if status_prop.get("type") == "status" and status_prop.get("status"):
            status = status_prop["status"]["name"]
        else:
            status = "UNKNOWN"

        mapping[proj_id] = {"name": name, "status": status}

    return mapping


# -------------------------------
# Get tasks scheduled for next week
# -------------------------------
def extract_date_from_task(props):
    """
    Your DB uses several different date fields depending on the task.
    We check them in priority order.
    """

    # 1. Task Date field
    d = props.get("Date", {}).get("date")
    if d:
        return d

    # 2. Due date
    d = props.get("Due", {}).get("date")
    if d:
        return d

    # 3. Completed on
    d = props.get("Completed on", {}).get("date")
    if d:
        return d

    # No usable date
    return None


def get_tasks_for_next_week(project_map):
    now = datetime.now().date()
    week_from_now = now + timedelta(days=7)

    rows = query_db(TASKS_DB)
    grouped = {}

    for t in rows:
        props = t.get("properties", {})

        date_prop = extract_date_from_task(props)
        if not date_prop:
            continue

        start_raw = date_prop.get("start")
        end_raw = date_prop.get("end") or start_raw

        if not start_raw:
            continue

        try:
            start = parse_date(start_raw).date()
            end = parse_date(end_raw).date()
        except Exception:
            continue

        if end < now or start > week_from_now:
            continue

        # project relation
        project_rel = props.get("Project", {}).get("relation", [])
        if not project_rel:
            continue
        project_id = project_rel[0]["id"]

        # Get project metadata
        proj_info = project_map.get(project_id, {})
        project_name = proj_info.get("name", "(Unknown project)")
        project_status = proj_info.get("status", "UNKNOWN")

        # Get task title
        title = props.get("Task name", props.get("Name", {}))
        title_list = title.get("title", [])
        name = title_list[0]["plain_text"] if title_list else "(No name)"

        grouped.setdefault(project_status, {}).setdefault(project_name, []).append(
            {"name": name, "start": str(start), "end": str(end)}
        )

    return grouped


# -------------------------------
# Format output
# -------------------------------
def format_report(grouped, benty=False):
    CUSTOM_ORDER = [
        "Working actively",
        "Writing",
        "Preparation",
        "In Review",
        "Backlog",
        "Done",
        "Canceled",
    ]

    def sort_key(status):
        return CUSTOM_ORDER.index(status) if status in CUSTOM_ORDER else 999

    lines = []
    lines.append(f"<@{MY_USER}>")

    if benty:
        lines.append(add_BentyFields())
        lines.append("\n")

    lines.append("*STATUS UPDATE*")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    if not grouped:
        lines.append("_No tasks scheduled for the upcoming week._")
        return "\n".join(lines)

    for status in sorted(grouped.keys(), key=sort_key):
        if status not in skip_status:
            lines.append(f"\n*{status}*")

            for project_name in sorted(grouped[status].keys()):
                lines.append(f"• *{project_name}*")

                tasks_sorted = sorted(
                    grouped[status][project_name], key=lambda t: t["start"]
                )

                for t in tasks_sorted:
                    lines.append(f"    • {t['name']}  ({t['start']} → {t['end']})")

    return "\n".join(lines)


# -------------------------------
# Main
# -------------------------------
def main():
    projects = get_projects()
    grouped = get_tasks_for_next_week(projects)
    report = format_report(grouped, benty=True)

    print(report)  # still print locally if running manually

    # Send to Slack
    if "SLACK_WEBHOOK_URL" in os.environ:
        send_to_slack(report)
    else:
        print("\n[Slack disabled — no SLACK_WEBHOOK_URL environment variable]")


if __name__ == "__main__":
    main()
