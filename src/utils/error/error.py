class CustomException(Exception):
    """A simple custom exception class.

    # Example:
    try:
        raise CustomException("A custom error occurred")
    except CustomException as e:
        print(e)
    """

    def __init__(self, message):
        """
        Initialize CustomException.

        Args:
            message (str): The error message.
        """
        super().__init__(message)
        self.message = message

    def __str__(self):
        """
        Return the string representation of the exception.

        Returns:
            str: The error message.
        """
        return self.message
