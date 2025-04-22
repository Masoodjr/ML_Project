import random
import pandas as pd

def generate_value_analysis(programs):
    analysis = []
    for _, program in programs.iterrows():
        analysis.append({
            'university_id': program['university_id'],
            'program_id': program['program_id'],
            'value_score': round(random.uniform(3.0, 9.5), 2),
            'roi_5years': random.randint(50000, 300000),
            'break_even_years': round(random.uniform(3, 10), 1)
        })
    return pd.DataFrame(analysis)