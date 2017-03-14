class Error(Exception):
    pass


class ConnectException(Error):
    pass


class PrintException(Error):
    pass


class PasswordException(Error):
    pass


class ConfigurationException(Error):
    pass
