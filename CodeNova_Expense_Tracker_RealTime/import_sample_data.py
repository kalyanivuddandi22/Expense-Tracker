import csv
from decimal import Decimal
from app import init_db, get_db, BASE_DIR

init_db()
with get_db() as db:
    if db.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]:
        print("Database already contains transactions; sample import skipped.")
    else:
        with (BASE_DIR / "sample_transactions.csv").open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                cents = int(Decimal(row["amount"]) * 100)
                db.execute("INSERT INTO transactions(date,type,category,amount_cents,description) VALUES(?,?,?,?,?)",
                           (row["date"], row["type"], row["category"], cents, row["description"]))
        db.commit()
        print("Sample transactions imported.")
