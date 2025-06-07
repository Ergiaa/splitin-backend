class CustomError(Exception):
    def __init__(self, message="An error occurred", status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return f"{self.status_code}: {self.message}"
