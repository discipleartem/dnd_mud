from messages import Messages


class ErrorHandler:
    @staticmethod
    def log_error(message: str) -> None:
        """Handle error by printing a message."""
        ErrorHandler._print_message(message)

    @staticmethod
    def log_error_message_static(message: str) -> None:
        """Log an error message."""
        ErrorHandler.log_error(message)

    @staticmethod
    def handle_error(e: Exception) -> None:
        """Handle errors."""
        ErrorHandler._print_message(f"{Messages.ERROR_OCCURRED}{e}")

    @staticmethod
    def log_key_not_found_error(key_name: str) -> None:
        ErrorHandler._print_message(Messages.ERROR_MESSAGE_KEY_NOT_FOUND.format(key_name))

    @staticmethod
    def _print_message(message: str) -> None:
        """Print a message."""
        print(message)
