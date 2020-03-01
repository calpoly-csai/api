import requests  # noqa
import json

BASE_URL = "http://0.0.0.0:8080"
URL = f"{BASE_URL}/new_data/calendars"


# TODO: assert other properties like
#       * if data already exists in database, then no update
#       * if given bad data values then response.status_code == bad
#       * if given missing data keys then ...
#       * if given ....... ????


def test_post_one_calendar():
    data = {
        "calendars": [
            {
                "date": "7_4_2020",
                "day": "4",
                "month": "July",
                "year": "2020",
                "raw_events_text": ["TEST EVENT"],
            }
        ]
    }

    # aka 'request body' aka 'payload'
    request_json = json.dumps(data)

    headers = {"Content-Type": "application/json"}
    print("request_json:\n\n", request_json, "\n")
    response = requests.post(URL, data=request_json, headers=headers)

    # printouts
    print("response.ok", response.ok)
    print("response.status_code", response.status_code)
    print("response.text", response.text)

    # assertions
    assert response.ok is True
    assert response.status_code == 200
    assert response.text == "SUCCESS"

