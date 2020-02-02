import time


class Validator:

    def __init__(self):
        super().__init__()

    def validate(self, data):
        """Takes in a dictionary of data and returns a dictionary of issues"""
        return data

    def fix(self, data, issues):
        """
        Takes measures to fill in missing data in form, cloning, mutating and then returning the data.
        If not possible, raises error.
        """
        return data


class WakeWordValidator(Validator):
    """Ensures that the form metadata recieved from the REST API for the Wake Word audio is valid."""

    def __init__(self, validators=None):
        super().__init__()
        self.validators = validators or {
            'isWakeWord':
                lambda val: type(val) == str and
                (val == 'true' or val == 'false'),
            'noiseLevel':
                lambda level: type(level) == str and level in 'qml' and len(
                    level) == 1,
            'tone':
                lambda tone: type(tone) == str,
            'location':
                lambda location: type(location) == str,
            'gender':
                lambda gender: type(gender) == str and gender in 'mf' and len(
                    gender) == 1,
            'lastName':
                lambda lastName: type(lastName) == str,
            'firstName':
                lambda firstName: type(firstName) == str,
            'timestamp':
                lambda timestamp: str.isdigit(timestamp),
            'username':
                lambda username: type(username) == str,
        }

    def validate(self, data):
        """
        Checks if the Wake Word audio metadata is complete and in its correct form.
        Returns array of issues.
        """
        issues = {}
        for key in self.validators:
            validator = self.validators[key]
            try:
                val = data[key]
            except:
                issues[key] = 'DNE'
            if (not validator(val)):
                issues[key] = 'invalid'
        return issues

    def fix(self, data, issues):
        """
        Attempts to fix Wake Word audio metadata.
        If the data issue is irreplaceable, raises ValueError.
        """
        form = data.copy()
        for key in issues:
            issue = issues[key]
            if (issue == 'DNE'):
                if (key == 'username'):
                    form[key] = 'guest'
                elif (key == 'timestamp'):
                    form[key] = int(time.time())
                    print('fixed timestamp', form[key])
                else:
                    raise ValueError(
                        f"Required audio metadata '{key}' was not provided")
            elif (issue == 'invalid'):
                # TODO: anticipate invalid entries and correct them.
                raise ValueError(
                    f"{key} has invalid value of {form[key]} with a type of {type(form[key])}"
                )
        return form
