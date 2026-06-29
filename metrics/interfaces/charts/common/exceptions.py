class InvalidFileFormatError(Exception):
    def __init__(self):
        message = "Invalid file format, must be `svg`"
        super().__init__(message)
