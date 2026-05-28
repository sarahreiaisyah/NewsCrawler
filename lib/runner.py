from datetime import date, timedelta
import subprocess
import os

start_date = date(2025, 2, 1)
end_date = date(2025, 8, 18)
portal = "CNBC"

base_dir = os.path.dirname(os.path.abspath(__file__))
crawler_path = os.path.join(base_dir, "crawler.py")

while start_date <= end_date:
    subprocess.run(["python", crawler_path, "--date", str(start_date), "--portal", portal
    ])
    start_date += timedelta(days=1)
