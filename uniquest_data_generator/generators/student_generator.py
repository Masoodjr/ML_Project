import pandas as pd
import random
from .base_generators import *
from config import (NUM_STUDENTS, DIRTY_DATA_PROBABILITY, DUPLICATE_PROBABILITY,
                   MIN_STUDENT_AGE, MAX_STUDENT_AGE, MISSING_DATA_PROBABILITY)

def generate_students():
    students = []
    for _ in range(NUM_STUDENTS):
        # Create clean student record
        clean_data = {
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

        # Randomly decide if we'll create a dirty record
        if random.random() < DIRTY_DATA_PROBABILITY:
            dirty_type = random.choice(['missing', 'invalid', 'outlier'])
            
            if dirty_type == 'missing':
                # Create record with missing values
                student = {
                    **clean_data,
                    'email': None,
                    'gre_score': None if random.random() < MISSING_DATA_PROBABILITY else clean_data['gre_score'],
                    'toefl_score': None if random.random() < MISSING_DATA_PROBABILITY else clean_data['toefl_score'],
                    'gpa': None if random.random() < MISSING_DATA_PROBABILITY else clean_data['gpa']
                }
            elif dirty_type == 'invalid':
                # Create record with invalid values
                student = {
                    **clean_data,
                    'email': 'invalid_email',
                    'gre_score': random.randint(100, 259),  # Below valid range
                    'toefl_score': random.randint(121, 150),  # Above valid range
                    'gpa': round(random.uniform(4.1, 5.0), 2),  # Above valid range
                    'work_experience': -5,  # Negative value
                    'phone': '123',  # Invalid format
                    'financial_status': 'Unknown'  # Invalid value
                }
            elif dirty_type == 'outlier':
                # Create record with outlier values
                student = {
                    **clean_data,
                    'gre_score': 340,  # Perfect score
                    'toefl_score': 120,  # Perfect score
                    'gpa': 4.0,  # Perfect GPA
                    'work_experience': 120,  # 10 years (unusual for student)
                    'date_of_birth': fake.date_of_birth(
                        minimum_age=40,  # Older than typical student
                        maximum_age=50
                    )
                }
        else:
            # Use clean data
            student = clean_data
        
        students.append(student)
    
    # Add duplicates (5% of records)
    num_duplicates = int(NUM_STUDENTS * DUPLICATE_PROBABILITY)
    students.extend(random.choices(students, k=num_duplicates))
    
    # Create DataFrame
    df = pd.DataFrame(students)
    
    # Ensure student_id is unique even with duplicates
    df['student_id'] = range(1, len(df) + 1)
    
    return df