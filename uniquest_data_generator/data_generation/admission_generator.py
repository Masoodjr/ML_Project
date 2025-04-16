import pandas as pd
from .base_generators import *
from config import APPLICATION_YEAR

def generate_admissions(programs):
    admissions = []
    for prog_id, prog_row in programs.iterrows():
        admission = {
            'program_id': prog_id + 1,
            'university_id': prog_row['university_id'],
            'min_gre': max(260, random_gre() - random.randint(0, 20)),
            'min_toefl': max(60, random_toefl() - random.randint(0, 15)),
            'min_gpa': max(2.5, round(random_gpa() - 0.3, 2)),
            'required_work_experience': random.randint(0, 12),
            'admission_year': APPLICATION_YEAR,
            'avg_admitted_gre': random_gre(),
            'avg_admitted_gpa': random_gpa(),
            'acceptance_rate': round(random.uniform(5, 50), 2)
        }
        admissions.append(admission)
    
    df = pd.DataFrame(admissions)
    df['admission_id'] = range(1, len(df) + 1)
    return df