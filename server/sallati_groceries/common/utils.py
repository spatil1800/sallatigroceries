import secrets
import string


def generate_random_id(N):
    # Generate random string of length N.
    random_id = "".join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(N)
    )
    return random_id


class UnitConverter:
    CONVERSIONS = {
        "TiB": {"TB": 1.099511628},
        "TB": {"TiB": 0.909494702},
        "KiB": {"KB": 1.024},
        "KB": {"KiB": 0.9765625},
        "MiB/s": {"TiB/s": 0.0000009537},
        "TiB/s": {"MiB/s": 1048576},
    }

    @classmethod
    def convert(cls, value, from_unit, to_unit, precision=2):

        c_factor = cls.CONVERSIONS.get(from_unit, {}).get(to_unit, None)
        if c_factor:
            return round(value * c_factor, precision)
        else:
            return None
