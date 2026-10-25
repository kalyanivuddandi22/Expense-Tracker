from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
from datetime import datetime
from decimal import Decimal, InvalidOperation
import sqlite3, csv, io

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "expenses.db"
app = Flask(__name__)
DATE_FORMAT = "%Y-%m-%d"
CATEGORIES = ["Food", "Utilities", "Travel", "Shopping", "Education", "Health",
              "Salary", "Freelance", "Entertainment", "Housing", "Other"]

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with get_db() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('Income','Expense')),
            category TEXT NOT NULL,
            amount_cents INTEGER NOT NULL CHECK(amount_cents > 0),
            description TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
        db.commit()

def validate_date(value):
    try:
        parsed = datetime.strptime(value, DATE_FORMAT)
        if parsed.strftime(DATE_FORMAT) != value: raise ValueError
        return value
    except (ValueError, TypeError):
        raise ValueError("Enter a valid date in YYYY-MM-DD format.")

def to_cents(raw):
    try:
        amount = Decimal(str(raw).strip())
        if not amount.is_finite() or amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        if amount.as_tuple().exponent < -2:
            raise ValueError("Use no more than two decimal places.")
        return int((amount * 100).quantize(Decimal("1")))
    except (InvalidOperation, AttributeError):
        raise ValueError("Enter a valid amount, such as 250 or 250.50.")

def row_dict(row):
    result = dict(row)
    result["amount"] = result.pop("amount_cents") / 100
    return result

def date_filters():
    start, end = request.args.get("start", "").strip(), request.args.get("end", "").strip()
    clauses, values = [], []
    if start:
        validate_date(start); clauses.append("date >= ?"); values.append(start)
    if end:
        validate_date(end); clauses.append("date <= ?"); values.append(end)
    if start and end and start > end:
        raise ValueError("Start date must be on or before end date.")
    return clauses, values

@app.route("/")
def index():
    return render_template("index.html", categories=CATEGORIES)

@app.get("/api/transactions")
def transactions():
    try:
        clauses, values = date_filters()
        category = request.args.get("category", "").strip()
        kind = request.args.get("type", "").strip()
        if category: clauses.append("LOWER(category)=LOWER(?)"); values.append(category)
        if kind:
            if kind not in ("Income", "Expense"): raise ValueError("Invalid transaction type.")
            clauses.append("type=?"); values.append(kind)
        sql = "SELECT * FROM transactions" + ((" WHERE " + " AND ".join(clauses)) if clauses else "")
        sql += " ORDER BY date DESC, id DESC"
        with get_db() as db: rows = db.execute(sql, values).fetchall()
        return jsonify([row_dict(row) for row in rows])
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.get("/api/summary")
def summary():
    try:
        clauses, values = date_filters()
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        with get_db() as db:
            totals = db.execute("SELECT type, COALESCE(SUM(amount_cents),0) total FROM transactions" + where + " GROUP BY type", values).fetchall()
            cats_sql = "SELECT category, SUM(amount_cents) total FROM transactions" + where + (" AND " if where else " WHERE ") + "type='Expense' GROUP BY category ORDER BY total DESC"
            cats = db.execute(cats_sql, values).fetchall()
            count = db.execute("SELECT COUNT(*) FROM transactions" + where, values).fetchone()[0]
        totals = {r["type"]: r["total"] for r in totals}
        income, expense = totals.get("Income", 0), totals.get("Expense", 0)
        return jsonify({"income": income/100, "expenses": expense/100, "balance": (income-expense)/100,
                        "count": count, "categories": [{"category": r["category"], "amount": r["total"]/100} for r in cats]})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.post("/api/transactions")
def add_transaction():
    data = request.get_json(silent=True) or {}
    try:
        date = validate_date(str(data.get("date", "")).strip())
        kind = str(data.get("type", "")).strip()
        if kind not in ("Income", "Expense"): raise ValueError("Choose Income or Expense.")
        category = str(data.get("category", "")).strip()
        if not category or len(category) > 60: raise ValueError("Category is required (maximum 60 characters).")
        description = str(data.get("description", "")).strip()
        if len(description) > 250: raise ValueError("Description must be 250 characters or fewer.")
        cents = to_cents(data.get("amount", ""))
        with get_db() as db:
            cur = db.execute("INSERT INTO transactions(date,type,category,amount_cents,description) VALUES(?,?,?,?,?)",
                             (date, kind, category, cents, description))
            db.commit()
            row = db.execute("SELECT * FROM transactions WHERE id=?", (cur.lastrowid,)).fetchone()
        return jsonify(row_dict(row)), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.delete("/api/transactions/<int:transaction_id>")
def delete_transaction(transaction_id):
    with get_db() as db:
        cur = db.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
        db.commit()
    if not cur.rowcount: return jsonify({"error": "Transaction not found."}), 404
    return jsonify({"message": "Deleted."})

@app.get("/api/export")
def export_csv():
    try:
        clauses, values = date_filters()
        sql = "SELECT id,date,type,category,amount_cents,description FROM transactions" + ((" WHERE " + " AND ".join(clauses)) if clauses else "")
        sql += " ORDER BY date DESC, id DESC"
        with get_db() as db: rows = db.execute(sql, values).fetchall()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id","date","type","category","amount","description"])
        for r in rows: writer.writerow([r["id"],r["date"],r["type"],r["category"],f'{r["amount_cents"]/100:.2f}',r["description"]])
        return send_file(io.BytesIO(output.getvalue().encode("utf-8-sig")), mimetype="text/csv",
                         as_attachment=True, download_name="expense_report.csv")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.get("/api/health")
def health(): return jsonify({"status":"ok"})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
