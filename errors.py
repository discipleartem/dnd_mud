from messages import Messages


class ErrorHandler:
    @staticmethod
    def log_error(message: str) -> None:
        """Handle error by printing a message."""
        print(message)

    @staticmethod
    def log_error_message(message: str) -> None:
        """Log an error message."""
        ErrorHandler.log_error(message)  # Corrected the method call

    @staticmethod
    def handle_error(e: Exception) -> None:
        """Handle errors."""
        print(f"{Messages.ERROR_OCCURRED}{e}")