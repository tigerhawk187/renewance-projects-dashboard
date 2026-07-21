#!/usr/bin/env python3
"""
Renewance Active Projects - Lift (Quickbase) pull.
Runs in GitHub Actions on a weekday 4am CT cron. Reads the Quickbase user
token from the QB_USER_TOKEN secret, pulls active projects + expenses +
recent daily reports, computes labor/materials burn and critical items,
and writes data/projects.js (window.DASHBOARD = {...}) for the dashboard.

Pure standard library - no pip install needed.
"""
import os, json, re, datetime, urllib.request

REALM = os.environ.get("QB_REALM", "lift.quickbase.com")
APP = "btctjiyp3"
T_PROJECTS = "btcwcxxv2"
T_EXPENSES = "btcwcub5k"
T_DAILY = "btdnzrmkr"
TOK = os.environ["QB_USER_TOKEN"]

def api(path, body):
    req = urllib.request.Request("https://api.quickbase.com/v1/" + path,
        data=json.dumps(body).encode(), method="POST")
    req.add_header("QB-Realm-Hostname", REALM)
    req.add_header("Authorization", "QB-USER-TOKEN " + TOK)
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "RenewanceDashboard/1.0")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())

def v(rec, f): return rec.get(str(f), {}).get("value")
def h(x):
    try: return round(float(x) / 3600000.0, 1)
    except Exception: return None
def strip(s):
    if not s: return ""
    s = re.sub(r"<[^>]+>", " ", str(s))
    s = re.sub(r"&nbsp;|&amp;|&#160;", " ", s)
    return re.sub(r"\s+", " ", s).strip()

# Lift's field 114 (Project Management Alerts) emits generic formula boilerplate
# like "Alert: % Hours Assigned is greater than 1! Alert: % Hours Worked is
# greater than 1!" - no project name, no numbers, and it duplicates the
# contract-aware burn bar the dashboard already computes. Drop those clauses;
# keep any substantive alert text Lift may put in the same field.
GENERIC_ALERT = re.compile(r"%\s*hours\s+(assigned|worked)\s+is\s+greater\s+than\s+1", re.I)
def clean_pm_alert(s):
    if not s: return ""
    parts = re.split(r"(?i)\balert:\s*", s)
    keep = []
    for part in parts:
        part = part.strip().strip("!").strip()
        if not part or GENERIC_ALERT.search(part):
            continue
        keep.append(part)
    return "; ".join(keep)

today = datetime.date.today()
d_dr = (today - datetime.timedelta(days=45)).isoformat()
d_exp = (today - datetime.timedelta(days=180)).isoformat()

ACTIVE = ["Ongoing", "In Progress", "Scheduled", "Not Scheduled", "Pipeline"]
where_active = "OR".join("{30.EX.'%s'}" % s for s in ACTIVE)

# 1) Active projects
pj = api("records/query", {"from": T_PROJECTS,
    "select": [3,6,30,32,11,8,21,22,23,107,108,116,117,146,86,114,115,125,140,141,143,43,104],
    "where": where_active, "options": {"top": 800}})
projects = {}
for r in pj["data"]:
    rid = v(r,3); wo = v(r,6) or ""
    cust = v(r,32) or v(r,11) or ""
    internal = (cust.strip().lower() == "renewance") or cust.strip() == ""
    aH, wH = h(v(r,107)), h(v(r,108))
    burn = round(wH/aH*100) if (aH and wH and aH > 0) else None
    projects[rid] = {
        "id": str(rid), "recordId": rid, "code": wo, "name": v(r,8) or v(r,11) or wo,
        "customer": cust, "status": v(r,30) or "", "internal": bool(internal),
        "pm": v(r,125) or "", "segment": v(r,140) or "", "txn": v(r,141) or "",
        "startDate": v(r,21), "endDate": v(r,22), "firstWorked": v(r,116), "lastWorked": v(r,117),
        "labor": {"assignedHours": aH or 0, "workedHours": wH or 0, "burnPct": burn},
        "materials": {"spent": 0.0, "budget": None, "dealAmount": v(r,146)},
        "scope": strip(v(r,115)), "summary": strip(v(r,23)), "pmAlerts": clean_pm_alert(strip(v(r,114))),
        "lastReport": None, "progress": "", "reports": [], "critical": []
    }

# 2) Expenses (180d) summed per project
try:
    ex = api("records/query", {"from": T_EXPENSES, "select": [3,28,15],
        "where": "{22.OAF.'%s'}" % d_exp, "options": {"top": 5000}})
    for r in ex["data"]:
        pid = v(r,28)
        if pid in projects:
            projects[pid]["materials"]["spent"] += float(v(r,15) or 0)
except Exception as e:
    print("EXPENSE_WARN", e)

# 3) Daily reports (45d) grouped per project
try:
    dr = api("records/query", {"from": T_DAILY, "select": [3,6,25,15,16,111,86,57,87],
        "where": "{25.OAF.'%s'}" % d_dr, "sortBy": [{"fieldId": 25, "order": "DESC"}],
        "options": {"top": 4000}})
    for r in dr["data"]:
        pid = v(r,6)
        if pid not in projects: continue
        p = projects[pid]
        if not p["lastReport"]: p["lastReport"] = v(r,25)
        if len(p["reports"]) < 4:
            p["reports"].append({"date": v(r,25), "hours": v(r,86), "techs": v(r,57),
                "text": strip(v(r,15))[:600], "issues": strip(v(r,16))[:400],
                "requests": strip(v(r,111))[:400]})
except Exception as e:
    print("DAILY_WARN", e)

# 4) Progress + critical items
for p in projects.values():
    latest = p["reports"][0] if p["reports"] else None
    p["progress"] = (latest["text"] if latest and latest["text"] else p["scope"] or p["summary"])[:600]
    c = []
    if p["pmAlerts"]:
        c.append({"sev": "amber", "type": "PM alert", "text": p["pmAlerts"][:300], "meta": "Lift - Project Management Alerts"})
    for rep in p["reports"][:3]:
        if rep["requests"]:
            c.append({"sev": "info", "type": "Customer request", "text": rep["requests"], "meta": "Daily report - %s" % rep["date"]})
        if rep["issues"]:
            c.append({"sev": "amber", "type": "Issue / jobs remaining", "text": rep["issues"], "meta": "Daily report - %s" % rep["date"]})
    p["critical"] = c[:8]

out = sorted(projects.values(), key=lambda x: (x["internal"], -(x["labor"]["workedHours"] or 0)))
meta = {"updated": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    "counts": {"total": len(out),
               "customer": sum(1 for p in out if not p["internal"]),
               "internal": sum(1 for p in out if p["internal"])}}
os.makedirs("data", exist_ok=True)
with open("data/projects.js", "w") as f:
    f.write("window.DASHBOARD = " + json.dumps({"meta": meta, "projects": out}, separators=(",", ":")) + ";")
print("WROTE data/projects.js -", meta["counts"])
