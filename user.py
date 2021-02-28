import logging


class User:
    def __init__(self, name, email, password):
        self.name = name
        self.logger = logging.getLogger(__name__)
        self.email = email
        self.password = password

    def __repr__(self):
        return f"User('{self.name}','{self.email})')"

