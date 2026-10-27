# ExpenseFlow 

A responsive, full-stack Expense Tracker built with **Python, Flask, SQLite, HTML, CSS, and JavaScript**. It meets the main CodeNova Task 2 requirements and adds a dashboard interface.

## Features
- Record income and expenses with date, category, amount, type, and description.
- Show total income, total expenses, net balance, and transaction count.
- Show category-wise expense totals using visual bars.
- Filter by start/end dates, category, and transaction type.
- Persist transactions in a local SQLite database.
- Export transaction history to CSV for Excel.
- Validate dates, types, positive amounts, and decimal precision.
- Delete transactions and automatically refresh dashboard totals.
- Responsive layout for desktop and mobile.
- Sample dataset included; no paid APIs or hosting required.

## Run on Windows
1. Extract the ZIP and open the `CodeNova_Expense_Tracker_RealTime` folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create a virtual environment (recommended):
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   If activation is blocked, you can skip activation and use `py -m pip` below.
4. Install Flask:
   ```powershell
   py -m pip install -r requirements.txt
   ```
5. Start the app:
   ```powershell
   py app.py
   ```
6. Open **http://127.0.0.1:5000** in your browser. Keep the terminal open while using it. Press `Ctrl+C` to stop the server.

## Sample data
Run `py import_sample_data.py` to load fictional demo transactions. The importer skips import if the database already has records.

## API endpoints
- `GET /api/transactions` — list transactions; optional `start`, `end`, `category`, `type`.
- `POST /api/transactions` — add a transaction.
- `DELETE /api/transactions/<id>` — delete a transaction.
- `GET /api/summary` — financial totals and category summaries.
- `GET /api/export` — download CSV.
- `GET /api/health` — health check.

## Project structure
```text
CodeNova_Expense_Tracker_RealTime/
├── app.py
├── requirements.txt
├── import_sample_data.py
├── sample_transactions.csv
├── README.md
├── data/                 # SQLite database is created here
├── templates/index.html
└── static/
    ├── style.css
    └── app.js
```

## Testing checklist
- Add income and expense; verify balance and category totals.
- Try negative, zero, malformed amounts; verify rejection.
- Try invalid dates and reversed date ranges; verify validation.
- Filter by date, category, and type.
- Restart server; verify records remain saved.
- Export CSV and open it in Excel.
- Delete a transaction and verify totals refresh.
- Resize browser to check mobile layout.

## GitHub
Create a public repository named `codenova-expense-tracker`. Upload the source files and README. Use only fictional data in a public repository. The `.gitignore` excludes local database files.

## Note
This local educational app does not connect to bank accounts or move money. The Flask development server is intended for local testing, not public production deployment.
