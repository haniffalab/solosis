#!/usr/bin/env python3

import random
import string

def generate_random_name(length=10):
    # Define the characters to choose from (letters and digits)
    characters = string.ascii_letters + string.digits
    # Generate a random name
    random_name = ''.join(random.choice(characters) for _ in range(length))
    return random_name
