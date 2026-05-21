from faker import Faker

__all__ = ["test_user_data"]

_fake = Faker()


test_user_data = {
    "subject": _fake.uuid4(),
    "organisation": _fake.uuid4(),
}
