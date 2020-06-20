class Entity:
    """
    An instance of an element in the Nimbus SQL Database.
    """

    __mapper_args__ = {
        "exclude_properties": [
            "validate",
            "format",
            "metadata",
            "get_data",
            "validators",
            "formatters",
        ]
    }

    def __init__(self, data):
        print("constructed Entity")
        self.validate(data)
        formatted_data = self.format(data)
        for key in formatted_data:
            setattr(self, key, formatted_data[key])

    def validate(self, data):
        """
        Checks if data has all required fields. Raises exception if data is misformed. 
        Note that you can have multiple validators to take in different data schemas.
        Parameters
        ----------
        `data:dict` Data to be validated, representing a single instance of the entity . 
        Raises
        -------
        Some type of Exception based on the problem with the data
        """
        pass

    def format(self, data) -> dict:
        """
        Casts data to correct types, assigns keys to match object.
        Parameters
        ----------
        `data:dict` Data to be formatted, representing a single instance of the entity. 
        Returns
        -------
        `dict` new data object which has been formatted.
        """
        pass

    def get_data(self):
        """
        Returns all fields that are related to table data.
        """
        pass

    def update(self, data: dict) -> bool:
        """
        Updates properties of the entity with the values in the `data` dict.
        Parameters
        ----------
        `data:dict` A subset of entity's properties to update. 
        """

    def __repr__(self):
        D = self.__dict__
        attributes = [
            f"{k}={D.get(k)}" for k in self.__dir__() if not k.startswith("_")
        ]
        attributes_string = ", ".join(attributes)
        return f"{self.__class__.__name__}({attributes_string})"
