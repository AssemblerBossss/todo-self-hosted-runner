class AuthError(Exception):
    """Base auth error"""


class UserAlreadyExists(AuthError):
    pass


class InvalidCredentials(AuthError):
    pass


class InactiveUser(AuthError):
    pass
