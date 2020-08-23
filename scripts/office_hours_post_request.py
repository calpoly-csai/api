import csv
import json
import requests
import sys


def convert_to_dict(data_in: list):
    """
    Takes a list of string lists which contains each row from
    a CSV and generates a dictionary of dictionaries which is
    each professor and their properties

    Args: 
            data_in (list of str lists)

    Returns:
            return_dict (dict of dicts)

    Ex:
    >> data_in = [[
                    "Smith, John",
                    "01-234",
                    "4567",
                    "jsmith@",
                    "10:00 - 12:00 PM",
                    "",
                    "10:00 - 12:00 PM",
                    "",
                    "10:00 - 12:00 PM"]
                ]

    >> oh_hours = convert_to_dict(data_in)
    >> oh_hours
       {

        "Smith, John": 
            {

                "Name":     "Smith, John"
                "Office":   "01-234"
                "Phone":    "4567"
                "Email":    "jsmith@"
                "Monday":   "10:00 - 12:00 PM"
                "Tuesday":  "",
                "Wednesday":"10:00 - 12:00 PM"
                "Thursday:  "",
                "Friday":   "10:00 - 12:00 PM" }
       }

    """

    # Dictionary of professors to be returned
    return_dict = {}

    try:

        # Parse each list of the input which is a row from the CSV
        for data in data_in:

            # Generate the office hours template dictionary
            office_hours_dict = {
                "Name": "",
                "Office": "",
                "Phone": "",
                "Email": "",
                "Monday": "",
                "Tuesday": "",
                "Wednesday": "",
                "Thursday": "",
                "Friday": "",
            }

            # Populate each property of the office hours dictionary
            office_hours_dict["Name"] = data[0]
            office_hours_dict["Office"] = data[1]
            office_hours_dict["Phone"] = data[2]
            office_hours_dict["Email"] = data[3]
            office_hours_dict["Monday"] = data[4]
            office_hours_dict["Tuesday"] = data[5]
            office_hours_dict["Wednesday"] = data[6]
            office_hours_dict["Thursday"] = data[7]
            office_hours_dict["Friday"] = data[8]

            # The key of the current professor of the professors dictionary
            # is the professor's name
            return_dict[data[0]] = office_hours_dict

        return return_dict

    except Exception as e:
        raise e


def process_csv(curr_file: str):
    """
    Reads in the CSV and outputs a list of string lists
    which is each row of the CSV

    Args:
        curr_file (str)

    Return:
        curr_data (list of str lists)

    Ex:
        >> out_list = process_csv("/path/to/office_hours.csv")
        >> out_list
            [[
                    "Smith, John",
                    "01-234",
                    "4567",
                    "jsmith@",
                    "10:00 - 12:00 PM",
                    "",
                    "10:00 - 12:00 PM",
                    "",
                    "10:00 - 12:00 PM"]
            ]
    """
    # List to be returned
    curr_data = []

    # Open the CSV and read the fields of the CSV
    with open(curr_file, "r") as csv_file:
        csvreader = csv.reader(csv_file)
        fields = next(csvreader)

        # Iterate through each row and append the row
        # to curr_data
        for row in csvreader:
            curr_data.append(row)

    return curr_data


def post_request(oh_dict: dict):
    """
    Takes in the dictionary of professors and
    sends the post request.

    Args:
        oh_dict (dict)

    Return:
        None

    Ex:
    >> oh_dict = 
        {
            "Smith, John" : 
            {
                "Name":     "Smith, John"
                "Office":   "01-234"
                "Phone":    "4567"
                "Email":    "jsmith@"
                "Monday":   "10:00 - 12:00 PM"
                "Tuesday":  "",
                "Wednesday":"10:00 - 12:00 PM"
                "Thursday:  "",
                "Friday":   "10:00 - 12:00 PM"}
       }
 
    >> post_request(oh_dict)

    """

    # URL for making the post request
    url = sys.argv[2]

    # Header contents for the post request
    headers = {"Content-Type": "application/json"}

    # Passes the professor dictionary through the post request
    x = requests.post(url, headers=headers, data=json.dumps(oh_dict))


if __name__ == "__main__":
    if (len(sys.argv) != 3) or (sys.argv[1][-3:] != "csv"):
        print(
            "Usage: python office_hours_post_request.py "
            '"/path/to/office_hours.csv" '
            '"http://post_request_url.com/new_data/office_hours"'
        )

    else:
        try:
            csv_data = process_csv(sys.argv[1])
            oh_dict = convert_to_dict(csv_data)
            post_request(oh_dict)

        except Exception as e:
            raise e
