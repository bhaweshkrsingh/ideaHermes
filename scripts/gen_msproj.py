#!/home/hermes/.venv/bin/python3
"""Generate MS Project XML (MSPDI) from /tmp/papers.json. Output: /tmp/ai-project-plan.xml"""
import json
from pathlib import Path
from datetime import date, timedelta

INPUT  = "/tmp/papers.json"
OUTPUT = "/tmp/ai-project-plan.xml"

papers = json.loads(Path(INPUT).read_text())
start_date = date.today()

def working_day(base, n):
    d, added = base, 0
    while added < n:
        base += timedelta(days=1)
        if base.weekday() < 5: added += 1
    return base

def fmt(d, t="08:00:00"): return f"{d.isoformat()}T{t}"

tasks_xml = []
uid = 1
summary_end = working_day(start_date, len(papers) * 3)
tasks_xml.append(f"""    <Task>
      <UID>0</UID><ID>0</ID><Name>Research Project</Name><Milestone>0</Milestone>
      <Summary>1</Summary><OutlineLevel>0</OutlineLevel>
      <Start>{fmt(start_date)}</Start><Finish>{fmt(summary_end,"17:00:00")}</Finish>
      <Duration>PT{len(papers)*3*8}H0M0S</Duration><DurationFormat>7</DurationFormat>
    </Task>""")

current = start_date
for i, p in enumerate(papers, 1):
    task_end = working_day(current, 2)
    review_end = working_day(current, 3)
    tasks_xml.append(f"""    <Task>
      <UID>{uid}</UID><ID>{uid}</ID><Name>Research: {p['title'][:80]}</Name>
      <Milestone>0</Milestone><Summary>1</Summary><OutlineLevel>1</OutlineLevel>
      <Start>{fmt(current)}</Start><Finish>{fmt(review_end,"17:00:00")}</Finish>
      <Duration>PT24H0M0S</Duration><DurationFormat>7</DurationFormat>
    </Task>"""); uid += 1
    tasks_xml.append(f"""    <Task>
      <UID>{uid}</UID><ID>{uid}</ID><Name>Literature search &amp; reading</Name>
      <Milestone>0</Milestone><Summary>0</Summary><OutlineLevel>2</OutlineLevel>
      <Start>{fmt(current)}</Start><Finish>{fmt(current,"17:00:00")}</Finish>
      <Duration>PT8H0M0S</Duration><DurationFormat>7</DurationFormat>
      <Notes>{p.get("summary","")[:200].replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")}</Notes>
    </Task>"""); uid += 1
    tasks_xml.append(f"""    <Task>
      <UID>{uid}</UID><ID>{uid}</ID><Name>Write summary</Name>
      <Milestone>0</Milestone><Summary>0</Summary><OutlineLevel>2</OutlineLevel>
      <Start>{fmt(task_end)}</Start><Finish>{fmt(task_end,"17:00:00")}</Finish>
      <Duration>PT8H0M0S</Duration><DurationFormat>7</DurationFormat>
    </Task>"""); uid += 1
    tasks_xml.append(f"""    <Task>
      <UID>{uid}</UID><ID>{uid}</ID><Name>Review &amp; sign-off</Name>
      <Milestone>1</Milestone><Summary>0</Summary><OutlineLevel>2</OutlineLevel>
      <Start>{fmt(review_end)}</Start><Finish>{fmt(review_end,"12:00:00")}</Finish>
      <Duration>PT4H0M0S</Duration><DurationFormat>7</DurationFormat>
    </Task>"""); uid += 1
    current = working_day(review_end, 1)

Path(OUTPUT).write_text(f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Project xmlns="http://schemas.microsoft.com/project">
  <Name>Research Project Plan</Name>
  <Title>Research Project Plan — {start_date.strftime('%B %d, %Y')}</Title>
  <StartDate>{fmt(start_date)}</StartDate>
  <FinishDate>{fmt(summary_end,'17:00:00')}</FinishDate>
  <DefaultStartTime>08:00:00</DefaultStartTime><DefaultFinishTime>17:00:00</DefaultFinishTime>
  <CalendarUID>1</CalendarUID>
  <Calendars><Calendar><UID>1</UID><Name>Standard</Name><IsBaseCalendar>1</IsBaseCalendar>
    <WeekDays>
      <WeekDay><DayType>1</DayType><DayWorking>0</DayWorking></WeekDay>
      <WeekDay><DayType>2</DayType><DayWorking>1</DayWorking><WorkingTimes><WorkingTime><FromTime>08:00:00</FromTime><ToTime>17:00:00</ToTime></WorkingTime></WorkingTimes></WeekDay>
      <WeekDay><DayType>3</DayType><DayWorking>1</DayWorking><WorkingTimes><WorkingTime><FromTime>08:00:00</FromTime><ToTime>17:00:00</ToTime></WorkingTime></WorkingTimes></WeekDay>
      <WeekDay><DayType>4</DayType><DayWorking>1</DayWorking><WorkingTimes><WorkingTime><FromTime>08:00:00</FromTime><ToTime>17:00:00</ToTime></WorkingTime></WorkingTimes></WeekDay>
      <WeekDay><DayType>5</DayType><DayWorking>1</DayWorking><WorkingTimes><WorkingTime><FromTime>08:00:00</FromTime><ToTime>17:00:00</ToTime></WorkingTime></WorkingTimes></WeekDay>
      <WeekDay><DayType>6</DayType><DayWorking>1</DayWorking><WorkingTimes><WorkingTime><FromTime>08:00:00</FromTime><ToTime>17:00:00</ToTime></WorkingTime></WorkingTimes></WeekDay>
      <WeekDay><DayType>7</DayType><DayWorking>0</DayWorking></WeekDay>
    </WeekDays>
  </Calendar></Calendars>
  <Tasks>
{chr(10).join(tasks_xml)}
  </Tasks>
</Project>
""", encoding="utf-8")
print(f"MS Project XML written to {OUTPUT} ({len(papers)} papers, {uid-1} tasks)")
