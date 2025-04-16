import pandas as pd
import random
from config import APPLICATIONS_PER_STUDENT, APPLICATION_YEAR
from .base_generators import *

def generate_applications(students, programs):
    applications = []
    student_ids = students['student_id'].tolist()
    program_records = programs.to_dict('records')
    statuses = ['submitted', 'under_review', 'accepted', 'rejected', 'waitlisted']
    
    for student_id in student_ids:
        num_apps = random.randint(
            APPLICATIONS_PER_STUDENT//2,
            APPLICATIONS_PER_STUDENT
        )
        selected_programs = random.sample(program_records, num_apps)
        for program in selected_programs:
            app_date = fake.date_between(
                start_date=f'{APPLICATION_YEAR-1}-01-01',
                end_date='today'
            )
            status = random.choice(statuses)
            decision_date = None
            if status in ['accepted', 'rejected', 'waitlisted']:
                decision_date = fake.date_between(
                    start_date=app_date,
                    end_date='today'
                )
            
            applications.append({
                'student_id': student_id,
                'program_id': program['program_id'],
                'application_date': app_date,
                'status': status,
                'decision_date': decision_date,
                'predicted_admission_probability': round(random.uniform(10, 90), 2),
                'actual_admission_probability': round(random.uniform(10, 90), 2),
                'notes': fake.sentence() if random.random() > 0.7 else None
            })
    
    df = pd.DataFrame(applications)
    df['application_id'] = range(1, len(df) + 1)
    return df