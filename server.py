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
from datetime import datetime
import json

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

@app.get("/time")
def convert_datetime(iso_time, display_format=None, iana=None, offset=None):

    # keep original value of iso_time parameter
    Original_iso_time = iso_time

    # Validate the existence of a parameter in the path

    # Validate that the parameter in the path is an ISO timestamp
    dt = parse_iso_time(iso_time)

    # convert datetime string from URL to datetime object
    iso_time = datetime.fromisoformat(iso_time)

    # Validate that the parameter in the path for "display_format" exists and is either "long" or "short"
    if display_format == "long":
        # convert to string
        iso_time = iso_time.strftime('%A, %B %d, %Y, %I:%M %p %Z')
    elif display_format == "short":
        # convert to string
        iso_time = iso_time.strftime('%b %d, %Y at %I:%M %p %Z')
    else:
        # if no display format is provided, convert to "long" string
        iso_time = iso_time.strftime('%A, %B %d, %Y, %I:%M %p %Z')

    # check if there are optional parameters for "offset" and  "iana"

    # convert output to data object
    json_formated_output = {
        "formatted": iso_time,
        "iso_time": Original_iso_time,
        "status": "200 OK"
    } 

    # Convert into JSON format
    json_data = json.dumps(json_formated_output)

    # return JSON formated object
    return {json_data}

# run this code as a standalone FastApi server from directly from Python
if __name__ == '__main__':
    # import FastAPI web server
    import uvicorn

    # launch this file in web server
    uvicorn.run(app)
