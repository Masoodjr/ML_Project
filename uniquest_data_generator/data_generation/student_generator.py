import pandas as pd
import random
from .base_generators import fake, random_gre, random_toefl, random_gpa, random_phone
from config import (NUM_STUDENTS, DIRTY_DATA_PROBABILITY, DUPLICATE_PROBABILITY,
                   MIN_STUDENT_AGE, MAX_STUDENT_AGE, MISSING_DATA_PROBABILITY)

def generate_students():
    """
    Generates a DataFrame of student records with:
    - Clean data (85% of records)
    - Dirty data (15% of records) with:
      - Missing values
      - Invalid values
      - Outliers
    - Duplicates (5% of total records)
    """
    students = []
    
    for _ in range(NUM_STUDENTS):
        # Base clean student record
        student = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'gre_score': random_gre(),
            'toefl_score': random_toefl(),
            'gpa': random_gpa(),
            'work_experience': random.randint(0, 60),  # months
            'preferred_location': fake.city(),
            'phone': random_phone(),
            'date_of_birth': fake.date_of_birth(
                minimum_age=MIN_STUDENT_AGE,
                maximum_age=MAX_STUDENT_AGE
            ),
            'financial_status': random.choice(['Low', 'Medium', 'High']),
            'loan_risk_score': round(random.uniform(1.0, 10.0), 2)
        }

        # Introduce data quality issues
        if random.random() < DIRTY_DATA_PROBABILITY:
            issue_type = random.choice(['missing', 'invalid', 'outlier'])
            
            if issue_type == 'missing':
                # Randomly nullify fields
                for field in ['email', 'gre_score', 'toefl_score', 'gpa']:
                    if random.random() < MISSING_DATA_PROBABILITY:
                        student[field] = None
                        
            elif issue_type == 'invalid':
                # Set invalid values
                student.update({
                    'email': 'invalid_email',
                    'gre_score': random.randint(100, 259),  # Below minimum
                    'toefl_score': random.randint(121, 150),  # Above maximum
                    'gpa': round(random.uniform(4.1, 5.0), 2),  # Above 4.0
                    'work_experience': -random.randint(1, 12),  # Negative
                    'phone': '123'  # Invalid format
                })
                
            elif issue_type == 'outlier':
                # Set extreme but possible values
                student.update({
                    'gre_score': 340,  # Perfect score
                    'toefl_score': 120,  # Perfect score
                    'gpa': 4.0,  # Perfect GPA
                    'work_experience': random.randint(72, 120),  # 6-10 years
                    'date_of_birth': fake.date_of_birth(
                        minimum_age=MAX_STUDENT_AGE + 5,
                        maximum_age=MAX_STUDENT_AGE + 15
                    )
                })

        students.append(student)
    
    # Add duplicates
    if DUPLICATE_PROBABILITY > 0:
        num_duplicates = int(NUM_STUDENTS * DUPLICATE_PROBABILITY)
        students.extend(random.choices(students, k=num_duplicates))
    
    # Create DataFrame
    df = pd.DataFrame(students)
    df['student_id'] = range(1, len(df) + 1)
    
    return df