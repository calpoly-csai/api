# import requests  # noqa
# import json

# BASE_URL = "http://0.0.0.0:8080"
# URL = f"{BASE_URL}/new_data/wakeword"
# WAVE_FILENAME = "happy.wav"

# # TODO: assert other properties like
# #       * if data already exists in database, then no update
# #       * if given bad data values then response.status_code == bad
# #       * if given missing data keys then ...
# #       * if given ....... ????


# def test_post_one_wakeword():
#     # TODO: make sure the pydrive.settings precondition is set betfore
#     #       running this
#     # read in a wav file as bytes
#     wav_file_binary = open(WAVE_FILENAME, "rb").read()

#     data = {
#         "isWakeWord": (None, "false"),
#         "noiseLevel": (None, "m"),
#         "tone": (None, "neutral"),
#         "emphasis": (None, "iss"),
#         "script": (None, "nimbus"),
#         "timestamp": (None, "1582932079"),
#         "location": (None, "Baker 110"),
#         "gender": (None, "m"),
#         "lastName": (None, "Aikens"),
#         "firstName": (None, "Miles"),
#         "wav_file": ("happy.wav", wav_file_binary),
#     }

#     # print("data:\n\n", data, "\n")
#     response = requests.post(URL, files=data)

#     # printouts
#     print("response.ok", response.ok)
#     print("response.status_code", response.status_code)
#     print("response.text", response.text)

#     # assertions
#     assert response.ok is True
#     assert response.status_code == 200
#     assert response.text == "SUCCESS"
