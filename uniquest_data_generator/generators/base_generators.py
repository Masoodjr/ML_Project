from faker import Faker
import random
import numpy as np
from .base_generators import *

fake = Faker()

def initialize_generators(seed):
    Faker.seed(seed)
    random.seed(seed)
    np.random.seed(seed)

def random_phone():
    return f"{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"

def random_date(start_date, end_date):
    return fake.date_between(start_date=start_date, end_date=end_date)

def random_gpa():
    return round(random.uniform(2.0, 4.0), 2)

def random_gre():
    return random.randint(260, 340)

def random_toefl():
    return random.randint(60, 120)