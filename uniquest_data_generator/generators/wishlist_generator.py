import pandas as pd
import random
from config import WISHLIST_ITEMS_PER_STUDENT
import faker

def generate_wishlist(students, programs):
    wishlist = []
    student_ids = students['student_id'].tolist()
    program_records = programs.to_dict('records')
    
    for student_id in student_ids:
        num_items = random.randint(
            WISHLIST_ITEMS_PER_STUDENT//2,
            WISHLIST_ITEMS_PER_STUDENT
        )
        selected_programs = random.sample(program_records, num_items)
        for priority, program in enumerate(selected_programs, 1):
            wishlist.append({
                'student_id': student_id,
                'program_id': program['program_id'],
                'priority': priority,
                'admission_probability': round(random.uniform(10, 90), 2),
                'predicted_salary': random.randint(40000, 120000),
                'value_score': round(random.uniform(3.0, 9.5), 2),
                'notes': faker.sentence() if random.random() > 0.7 else None
            })
    
    df = pd.DataFrame(wishlist)
    df['wishlist_id'] = range(1, len(df) + 1)
    return df