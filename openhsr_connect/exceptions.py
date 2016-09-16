class ConnectException(Exception):
    pass


class PrintException(ConnectException):
    pass


class PasswordException(ConnectException):
    pass


class ConfigurationException(ConnectException):
    pass
