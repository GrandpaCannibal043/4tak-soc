import random
import string
from .models import RegistrationCode

def generate_unique_code(length):
    while True:
        code = ''.join(random.choices(string.digits, k=length))
        if not RegistrationCode.objects.filter(code=code).exists():
            return code
