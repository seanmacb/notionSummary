📊 notionSummary

Automated weekly task summaries from Notion, delivered straight to Slack.

notionSummary is a lightweight Python tool that queries your Notion workspace, collects upcoming tasks, groups them by their parent project and status, and posts a clean weekly status update message to Slack. It is designed for researchers, software teams, and individuals who maintain structured project boards in Notion and want automated reporting.

⸻

✨ Features
	•	🧠 Queries Notion databases using the REST API
	•	🔗 Matches tasks to parent projects, using Notion relations
	•	📅 Filters tasks occurring in the next 7 days
	•	📂 Groups tasks by:
	•	Project status (e.g., “Working actively”, “Writing”, etc.)
	•	Project name
	•	🧹 Nicely formatted Slack output
	•	⚙️ Runs automatically via cron
	•	🔒 Uses standard environment variables for secret management

⸻

🗂 Project Structure

notionSummary/
│
├── weekly_status.py      # Main script: queries Notion + sends Slack update
├── README.md             # This file
└── ...                   # (optional supporting scripts)


⸻

🛠 Requirements
	•	Python 3.9+
	•	A Notion integration token with access to:
	•	Your Tasks database
	•	Your Projects database
	•	A Slack Incoming Webhook URL for posting updates

Install Python dependencies:

pip install requests python-dateutil


⸻

🔧 Configuration

Set environment variables for secrets and database IDs:

export NOTION_TOKEN="secret_..."
export TASKS_DB="<tasks_database_id>"
export PROJECTS_DB="<projects_database_id>"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/XXX/YYY/ZZZ"

You can add these to your .bashrc, .zshrc, or use a .env file and a loader.

⸻

🚀 Usage

Run the script manually:

python weekly_status.py

You’ll see output like:

STATUS UPDATE
Generated: 2025-12-07 18:44

## Working actively
• DESC Dark sirens, prep for LSST Y1
    • Data generation: NSBH’s (2025-10-01 → 2026-01-01)
    ...

If SLACK_WEBHOOK_URL is set, this same report is also sent to Slack.

⸻

📅 Cron Automation (optional)

To send weekly updates automatically, add a cron job:

crontab -e

Example: send every Monday at 9am:

0 9 * * MON /path/to/venv/bin/python /path/to/notionSummary/weekly_status.py >> /path/to/notionSummary/log.txt 2>&1

Make sure:
	•	Your environment variables are set in the cron environment
	•	You use the correct Python executable (from your virtualenv)

⸻

📝 How It Works
	1.	Query Notion Tasks database
The script uses the /v1/databases/<id>/query endpoint via requests.
	2.	Filter to next 7 days
Tasks are included if any part of their date range overlaps the next week.
	3.	Resolve parent project
For each task, the script dereferences the relation property "Project".
	4.	Query project metadata
Status and project title are extracted to determine grouping.
	5.	Group tasks
Tasks are grouped by:
	•	Project status (custom-sorted)
	•	Project name
	6.	Format Slack message
Output uses:
	•	bold headers
	•	bullet points
	•	indentation
(Slack-friendly Markdown)
	7.	POST to Slack webhook

⸻

🧪 Example Output in Slack

*STATUS UPDATE*
Generated: 2025-12-07 18:44

*Working actively*
• *DESC Dark sirens, prep for LSST Y1*
    • Data generation: NSBH’s  (2025-10-01 → 2026-01-01)
    • Data generation: BBH’s   (2025-10-01 → 2026-01-01)

• *LSST-Camera defect study*
    • Refactor code
    • Run SV analysis of historical defects


⸻

🧱 Extensibility

You can easily extend the script to:
	•	Create a Notion page for each weekly summary
	•	Upload a Markdown/PDF export to Notion or Slack
	•	Filter by task tags or priorities
	•	Include overdue tasks
	•	Sort tasks by priority or date

If you want help adding these, just ask!

⸻

📄 License

MIT License — feel free to use, modify, and extend.

⸻

If you’d like, I can also generate:
	•	A project icon
	•	GitHub Actions CI workflow
	•	A requirements.txt or pyproject.toml
	•	A detailed troubleshooting section

Just let me know!
