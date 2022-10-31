import enum
class LicenseLevel(enum.Enum):
    STANDART = 'Standart'
    PRO = 'Pro'
    ENTERPRISE = 'Enterprise'

l=LicenseLevel

print(l.ENTERPRISE.value)