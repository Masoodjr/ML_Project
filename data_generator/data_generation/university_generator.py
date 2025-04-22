import pandas as pd
from .base_generators import random_date
from datetime import datetime
from config import NUM_UNIVERSITIES
from .base_generators import *

def generate_universities():
    universities = []
    for _ in range(NUM_UNIVERSITIES):
        uni = {
            'university_name': fake.unique.company() + " University",
            'location': fake.city() + ", " + fake.state_abbr(),
            'application_deadline': random_date(datetime(2024, 1, 1), datetime(2024, 12, 31)),
            'tier': random.choice(['Top', 'Mid', 'Low']),
            'avg_alumni_salary': random.randint(40000, 120000),
            'placement_rate': round(random.uniform(50, 95), 2),
            'value_score': round(random.uniform(3.0, 9.5), 2)
        }
        universities.append(uni)
    
    df = pd.DataFrame(universities)
    df['university_id'] = range(1, len(df) + 1)
    return df