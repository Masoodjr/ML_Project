import pandas as pd
import random
from config import MIN_PROGRAMS_PER_UNIVERSITY, MAX_PROGRAMS_PER_UNIVERSITY
from .base_generators import *

PROGRAM_NAMES = [
    "Computer Science", "Business Administration", "Electrical Engineering",
    "Biology", "Psychology", "Economics", "Mechanical Engineering",
    "Political Science", "Chemistry", "Mathematics", "English Literature",
    "History", "Physics", "Art", "Music"
]

def generate_programs(universities):
    programs = []
    for uni_id, uni_row in universities.iterrows():
        num_programs = random.randint(MIN_PROGRAMS_PER_UNIVERSITY, MAX_PROGRAMS_PER_UNIVERSITY)
        for _ in range(num_programs):
            program = {
                'university_id': uni_id + 1,
                'program_name': random.choice(PROGRAM_NAMES),
                'program_level': random.choice(['Undergraduate', 'Graduate']),
                'duration': random.choice([2, 4]),
                'tuition_fee': random.randint(5000, 50000),
                'avg_program_salary': random.randint(30000, 110000),
                'program_placement_rate': round(random.uniform(50, 95), 2),
                'description': fake.sentence()
            }
            programs.append(program)
    
    df = pd.DataFrame(programs)
    df['program_id'] = range(1, len(df) + 1)
    return df