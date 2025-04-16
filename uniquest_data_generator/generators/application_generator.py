import pandas as pd
import random
from config import APPLICATIONS_PER_STUDENT, APPLICATION_YEAR
from faker import Faker  # Make sure to import Faker
from datetime import datetime

# Initialize Faker instance
fake = Faker()

def generate_applications(students, programs):
    applications = []
    student_ids = students['student_id'].tolist()
    program_records = programs.to_dict('records')
    statuses = ['submitted', 'under_review', 'accepted', 'rejected', 'waitlisted']
    
    for student_id in student_ids:
        num_apps = random.randint(
            max(1, APPLICATIONS_PER_STUDENT//2),  # Ensure at least 1 application
            APPLICATIONS_PER_STUDENT
        )
        selected_programs = random.sample(program_records, min(num_apps, len(program_records)))
        
        for program in selected_programs:
            # Create datetime objects for date handling
            start_date = datetime(APPLICATION_YEAR-1, 1, 1)
            
            app_date = fake.date_between_dates(
                date_start=start_date,
                date_end=datetime.now()
            )
            
            status = random.choice(statuses)
            decision_date = None
            if status in ['accepted', 'rejected', 'waitlisted']:
                decision_date = fake.date_between_dates(
                    date_start=app_date,
                    date_end=datetime.now()
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