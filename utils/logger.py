class Logger:
    def __init__(self):
        pass  # You can add initialization code here if needed

    def error(self, message):
        """Log error messages in red"""
        print(f"\033[91m✗ {message}\033[00m")

    def info(self, message):
        """Log informational messages in blue"""
        print(f"\033[94mℹ️ {message}\033[00m")

    def success(self, message):
        """Log success messages in green"""
        print(f"\033[92m✓ {message}\033[00m")

    def warning(self, message):
        """Log warning messages in yellow"""
        print(f"\033[93m⚠️ {message}\033[00m")

    # For backward compatibility with your old print functions
    def prRed(self, message):
        """Alias for error logging (backward compatibility)"""
        self.error(message)

    def prGreen(self, message):
        """Alias for success logging (backward compatibility)"""
        self.success(message)

    def prYellow(self, message):
        """Alias for warning logging (backward compatibility)"""
        self.warning(message)