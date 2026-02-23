"""
Filename: server.py
Date Created: 2026-02-15

Description:
As a developer, I want to submit an ISO datetime value and receive a datetime value formatted string for display in either short form (Feb 15, 2026 8:00 AM) or long form (Sunday, February 15, 2026 8:00 AM).

Dependencies:
    - FastAPI
    - datetime


Example Expected API call format
    GET /time?iso_time=2026-02-11T16:00:00Z
    GET /time?iso_time=2026-02-11T16:00:00Z&iana=America/Los_Angeles&display_format=short 
    GET /time?iso_time=2026-02-11T16:00:00Z&offset=-08:00&display_format=long 

Instructions to Run FastAPI server
- you can run from Python (python server.py) or from FastAPI. The last lines of code in this file configure the server to run when called from python, rather than running "fastapi dev server.py" or "fastapi run server.py"

"""

from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta, timezone
import json
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

app = FastAPI()

@app.get("/")
def root_message():
    return {"Server is running"}

def parse_iso_time(iso_time):
    # replace "Z" with "+00:00" because "Z" is not understood by datetime object, but +00:00 is valid UTC time
    if iso_time.endswith("Z"):
        iso_time = iso_time.replace('Z', '+00:00')
    try:
        # https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat Accessed 18 February 2026
        dt = datetime.fromisoformat(iso_time)
    except ValueError:
        # https://fastapi.tiangolo.com/reference/exceptions/#fastapi.HTTPException Accessed 18 February 2026
        raise HTTPException(status_code=400, detail="Invalid ISO timestamp")
    return dt
# https://ucarion.com/rfc3339-in-any-language Accessed 18 February 2026
OFFSET_REGEX = re.compile(r"^([\+|-])(\d{2}):(\d{2})$")
def parse_offset(offset):
    # Check for format of offset (+/-00:00)
    match = OFFSET_REGEX.match(offset)
    if not match:
        raise HTTPException(status_code=400, detail="incorrect offset format")
    # Extract sign, mm, and hh from offset
    # https://docs.python.org/3/library/re.html#re.Match.groups Accessed 18 February 2026
    sign, hh, mm = match.groups()
    hours = int(hh)
    minutes = int(mm)
    # Calculate total minutes from offset
    total_minutes = (hours * 60) + minutes
    # Get a timedelta object
    # https://docs.python.org/3/library/datetime.html#timedelta-objects Accessed 19 February 2026
    delta_minutes = timedelta(minutes=total_minutes)
    # Change to negative value if sign is negative
    if sign == "-":
        delta_minutes = -delta_minutes
    # Get timezone object for timezone math later
    # https://docs.python.org/3/library/datetime.html#timezone-objects Accessed 19 February 2026
    return timezone(delta_minutes)

def format_datetime(dt, req_format):
    # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior Accessed 19 February 2026
    hour = dt.strftime("%I")
    minute = dt.strftime("%M")
    am_pm = dt.strftime("%p")

    if req_format == "short":
        return f"{dt.strftime('%b')} {dt.day}, {dt.strftime('%Y')}, {hour}:{minute} {am_pm}"
    else:
        return f"{dt.strftime('%A')}, {dt.strftime('%B')} {dt.day}, {dt.strftime('%Y')}, {hour}:{minute} {am_pm}"

@app.get("/time")
def convert_datetime(iso_time, display_format=None, iana=None, offset=None):

    # keep original value of iso_time parameter
    Original_iso_time = iso_time

    # Validate that the parameter in the path is an ISO timestamp
    dt = parse_iso_time(iso_time)

    # Check either iana or offset is provided
    # Chris updated to IF to allow for if display_format is provided, but not a value for iana or offset
    if iana is not None and offset is not None:
        raise HTTPException(status_code=400, detail="use iana or offset but not both")
    
    # Apply appropriate conversion using astimezone method
    # https://docs.python.org/3/library/datetime.html#datetime.datetime.astimezone Accessed 19 February 2026
    tz_used = None
    if iana is not None:
        try:
            # https://docs.python.org/3/library/zoneinfo.html Accessed 19 February 2026
            # NOTE: According to docs above Windows users may need to install tzdata
            dt = dt.astimezone(ZoneInfo(iana))
        except ZoneInfoNotFoundError:
            HTTPException(status_code=400, detail="ZoneInfo error")
        tz_used = iana
    elif offset is not None:
        dt = dt.astimezone(parse_offset(offset))
        tz_used = offset

    formatted = format_datetime(dt, display_format)

    # convert output to data object
    json_formated_output = {
        "formatted": formatted,
        "iso_time": Original_iso_time,
        "tz": tz_used
    }

    # return JSON formated object
    return json_formated_output

# run this code as a standalone FastApi server from directly from Python
if __name__ == '__main__':
    # import FastAPI web server
    import uvicorn

    # launch this file in web server
    uvicorn.run(app)
