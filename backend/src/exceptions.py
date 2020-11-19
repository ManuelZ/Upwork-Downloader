
class CredentialsNotFoundError(Exception):
    """ Raised if a there is a missing environment variable """
    def __str__(self):
        return "Error: Credentials file couldn't be accessed"
