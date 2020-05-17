import json
import pytest

from modules.validators import WakeWordValidator, WakeWordValidatorError
wake_word_data = {
"isWakeWord":"true",
"noiseLevel":"l",
"tone":"serious",
"location":"Cal Poly San Luis Obispo",
"gender":"m",
"lastName":"Waidhofer",
"firstName":"John",
"timestamp": "1589744893",
"username":"waidhofer",
"emphasis":"Emphasized",
"script":"testing 123",
"test":"foo"
}

important_fields = ["isWakeWord",
"noiseLevel",
"tone",
"location",
"gender",
"lastName",
"firstName",
"emphasis",
"script"]
def test_wake_word_missing_values():
    validator = WakeWordValidator()
    for field in important_fields:
        data = wake_word_data.copy()
        data.pop(field)
        issues = validator.validate(data)
        print(issues)

        assert len(issues) == 1

        with pytest.raises(WakeWordValidatorError):
            data = validator.fix(data,issues)
