import pandas as pd
import random
from config import (ALUMNI_RECORDS_PER_PROGRAM, GRADUATION_YEAR_RANGE,
                   MISSING_DATA_PROBABILITY)

JOB_SECTORS = [
    'Technology', 'Finance', 'Healthcare', 
    'Education', 'Government', 'Non-profit'
]

def generate_alumni_salary_data(programs, students):
    alumni = []
    student_records = students.to_dict('records')
    for prog_id, prog_row in programs.iterrows():
        num_records = random.randint(
            ALUMNI_RECORDS_PER_PROGRAM//2,
            ALUMNI_RECORDS_PER_PROGRAM
        )
        for _ in range(num_records):
            student = random.choice(student_records)
            alumni.append({
                'university_id': prog_row['university_id'],
                'program_id': prog_id + 1,
                'student_gre': student['gre_score'] if random.random() > MISSING_DATA_PROBABILITY else None,
                'student_gpa': student['gpa'] if random.random() > MISSING_DATA_PROBABILITY else None,
                'years_experience_pre_degree': random.randint(0, 10),
                'salary': random.randint(30000, 150000),
                'graduation_year': random.randint(*GRADUATION_YEAR_RANGE),
                'job_sector': random.choice(JOB_SECTORS)
            })
    
    df = pd.DataFrame(alumni)
    df['record_id'] = range(1, len(df) + 1)
    return df