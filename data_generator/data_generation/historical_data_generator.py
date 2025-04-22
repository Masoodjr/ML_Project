import pandas as pd
import random
from config import (HISTORICAL_RECORDS_PER_PROGRAM, HISTORICAL_YEAR_RANGE,
                   MISSING_DATA_PROBABILITY)

def generate_historical_admissions(programs, students):
    historical = []
    student_records = students.to_dict('records')
    for prog_id, prog_row in programs.iterrows():
        num_records = random.randint(
            HISTORICAL_RECORDS_PER_PROGRAM//2,
            HISTORICAL_RECORDS_PER_PROGRAM
        )
        for _ in range(num_records):
            student = random.choice(student_records)
            historical.append({
                'program_id': prog_id + 1,
                'university_id': prog_row['university_id'],
                'student_gre': student['gre_score'] if random.random() > MISSING_DATA_PROBABILITY else None,
                'student_toefl': student['toefl_score'] if random.random() > MISSING_DATA_PROBABILITY else None,
                'student_gpa': student['gpa'] if random.random() > MISSING_DATA_PROBABILITY else None,
                'student_work_experience': student['work_experience'] if random.random() > MISSING_DATA_PROBABILITY else None,
                'admission_result': random.choice(['Admitted', 'Rejected']),
                'admission_year': random.randint(*HISTORICAL_YEAR_RANGE)
            })
    
    df = pd.DataFrame(historical)
    df['record_id'] = range(1, len(df) + 1)
    return df