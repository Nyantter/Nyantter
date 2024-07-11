from . import User

class AuthorizedUser(User):
    email: str
    private_key: str

    def getUser(self) -> User:
        return User.model_validate(self)