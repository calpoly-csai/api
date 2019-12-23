
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
        form = data.copy()
        for key in form:
            if key == 'isWakeWord':
                form[key] = 'ww' if(form[key]) else 'nww'
            elif key == 'timestamp':
                form[key] = int(form[key])
            else:
                form[key] = form[key].lower().replace(' ', '-')
        return form
