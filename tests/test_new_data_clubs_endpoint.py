import requests  # noqa
import json

BASE_URL = "http://0.0.0.0:8080"
URL = f"{BASE_URL}/new_data/clubs"


def test_post_one_course():
    data = {
        "clubs": [
            {
                "club_name": "test_club",
                "types": "Academic, Special Interest",
                "desc": "description",
                "contact_email": "test@test.com",
                "contact_email_2": "test@test.com",
                "contact_person": "Test Person",
                "contact_phone": 15552223232,
                "box": 89,
                "advisor": "Test Person",
                "affiliation": None,
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
