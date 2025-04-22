import pandas as pd
import random
from config import PREDICTIONS_PER_STUDENT

def generate_admission_predictions(students, programs):
    predictions = []
    student_ids = students['student_id'].tolist()
    program_records = programs.to_dict('records')
    for student_id in student_ids:
        num_predictions = random.randint(1, PREDICTIONS_PER_STUDENT)
        selected_programs = random.sample(program_records, num_predictions)
        for program in selected_programs:
            predictions.append({
                'student_id': student_id,
                'university_id': program['university_id'],
                'program_id': program['program_id'],
                'admission_probability': round(random.uniform(10, 90), 2),
                'classification': random.choice(['Safe', 'Target', 'Reach']),
                'model_version': f"v{random.randint(1, 3)}.{random.randint(0, 5)}"
            })
    
    df = pd.DataFrame(predictions)
    df['prediction_id'] = range(1, len(df) + 1)
    return df

def generate_salary_predictions(students, programs):
    predictions = []
    student_ids = students['student_id'].tolist()
    program_records = programs.to_dict('records')
    for student_id in student_ids:
        num_predictions = random.randint(1, PREDICTIONS_PER_STUDENT)
        selected_programs = random.sample(program_records, num_predictions)
        for program in selected_programs:
            predictions.append({
                'student_id': student_id,
                'university_id': program['university_id'],
                'program_id': program['program_id'],
                'predicted_salary': random.randint(40000, 120000),
                'salary_percentile': random.randint(10, 90),
                'model_version': f"v{random.randint(1, 3)}.{random.randint(0, 5)}"
            })
    
    df = pd.DataFrame(predictions)
    df['prediction_id'] = range(1, len(df) + 1)
    return df