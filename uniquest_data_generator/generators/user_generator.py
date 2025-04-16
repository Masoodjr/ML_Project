import pandas as pd
import random
from config import NUM_STUDENTS
import faker

def generate_users(students):
    users = []
    student_ids = students['student_id'].tolist()
    
    # Create student users
    for student_id in student_ids:
        users.append({
            'student_id': student_id,
            'role': 'student',
            'username': faker.unique.user_name(),
            'password_hash': faker.sha256(raw_output=False),
            'last_login': faker.date_time_between(start_date='-1y', end_date='now')
        })
    
    # Create admin/advisor users (about 1% of student count)
    num_admins = max(50, NUM_STUDENTS // 100)
    for _ in range(num_admins):
        student_id = random.choice(student_ids)
        users.append({
            'student_id': student_id,
            'role': random.choice(['admin', 'advisor']),
            'username': faker.unique.user_name(),
            'password_hash': faker.sha256(raw_output=False),
            'last_login': faker.date_time_between(start_date='-1y', end_date='now')
        })
    
    df = pd.DataFrame(users)
    df['user_id'] = range(1, len(df) + 1)
    return df