import pandas as pd
import random
from config import RANKINGS_PER_PROGRAM

RANKING_SOURCES = [
    'QS World University', 'Times Higher Education',
    'US News', 'Forbes', 'Princeton Review'
]

RANKING_CATEGORIES = [
    'Overall', 'Research', 'Teaching',
    'Innovation', 'Employability'
]

def generate_ranking_data(programs):
    rankings = []
    for prog_id, prog_row in programs.iterrows():
        num_records = random.randint(1, RANKINGS_PER_PROGRAM)
        for _ in range(num_records):
            rankings.append({
                'university_id': prog_row['university_id'],
                'program_id': prog_id + 1,
                'program_rank': random.randint(1, 200),
                'ranking_year': random.randint(2018, 2024),
                'ranking_source': random.choice(RANKING_SOURCES),
                'ranking_category': random.choice(RANKING_CATEGORIES)
            })
    
    df = pd.DataFrame(rankings)
    df['ranking_id'] = range(1, len(df) + 1)
    return df