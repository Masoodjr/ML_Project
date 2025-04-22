import pandas as pd
import random
from config import FUNDING_RECORDS_PER_UNIVERSITY

FUNDING_SOURCES = [
    'Federal Grant', 'State Funding', 'Private Donation',
    'Corporate Sponsorship', 'Research Grant', 'Endowment'
]

def generate_funding_data(universities):
    funding = []
    for uni_id, _ in universities.iterrows():
        num_records = random.randint(
            FUNDING_RECORDS_PER_UNIVERSITY//2,
            FUNDING_RECORDS_PER_UNIVERSITY
        )
        for _ in range(num_records):
            funding.append({
                'university_id': uni_id + 1,
                'funding_source': random.choice(FUNDING_SOURCES),
                'amount': random.randint(10000, 5000000),
                'funding_year': random.randint(2015, 2024)
            })
    
    df = pd.DataFrame(funding)
    df['funding_id'] = range(1, len(df) + 1)
    return df