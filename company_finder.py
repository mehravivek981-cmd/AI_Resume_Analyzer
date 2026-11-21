import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMPANIES_FILE = os.path.join(BASE_DIR, "companies.csv")


def find_companies(job_role):
    """Return companies hiring for the given job role."""

    companies = []

    if not os.path.exists(COMPANIES_FILE):
        print("companies.csv not found!")
        return companies

    wanted = job_role.strip().lower()

    with open(COMPANIES_FILE, "r", encoding="utf-8-sig", newline="") as file:

        # skip blank lines so a stray empty first line cannot break the header
        rows = (line for line in file if line.strip())
        reader = csv.DictReader(rows)
        reader.fieldnames = [name.strip() for name in reader.fieldnames or []]

        for row in reader:

            if (row.get("Job_Role") or "").strip().lower() == wanted:

                companies.append({
                    "company": (row.get("Company_Name") or "").strip(),
                    "location": (row.get("Location") or "").strip(),
                    "description": (row.get("Description") or "").strip(),
                })

    return companies
