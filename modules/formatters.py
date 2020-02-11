class Formatter:
    """Formatter abstract class. Describes contract for all child formatters"""

    def __init__(self):
        super().__init__()

    def format(self, data):
        """Creates a copy of data, formats, and returns the formatted data"""
        return data


class WakeWordFormatter(Formatter):
    """Formats metadata for Wake Word audio"""

    def __init__(self):
        super().__init__()

    def format(self, data):
        # TODO: document this function better
        # TODO: write test cases for this function
        form = data.copy()
        form['isWakeWord'] = 'ww' if (form[key]) else 'nww'
        form["firstName"] = form["firstName"].title()
        form["lastName"] = form["lastName"].title()
        form['timestamp'] = int(form[key])

        return form
