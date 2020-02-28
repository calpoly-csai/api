import requests  # noqa
import json

BASE_URL = "http://0.0.0.0:8080"
URL = f"{BASE_URL}/new_data/courses"


def test_post_one_course():
    data = {
        "courses": [
            {
                "dept": "CPE",
                "courseNum": "357",
                "units": "4",
                "termsOffered": "F,W,SP",
                "courseName": "Systems Programming",
                "raw_concurrent_text": "N/A",
                "raw_recommended_text": "N/A",
                "raw_prerequisites_text": "CSC/CPE,102,and,CSC/CPE,103",
            }
        ]
    }

    # aka 'request body' aka 'payload'
    request_json = json.dumps(data)

    headers = {"Content-Type": "application/json"}
    print("request_json:\n\n", request_json, "\n")
    response = requests.post(URL, data=request_json, headers=headers)

    # assertions
    assert response.ok is True
    assert response.status_code == 200
    assert response.text == "SUCCESS"
