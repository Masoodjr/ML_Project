import pandas as pd
import os
from config import SEED
from generators.base_generators import initialize_generators
from generators.university_generator import generate_universities
from generators.student_generator import generate_students
from generators.program_generator import generate_programs
from generators.admission_generator import generate_admissions
from generators.historical_data_generator import generate_historical_admissions
from generators.alumni_generator import generate_alumni_salary_data
from generators.funding_generator import generate_funding_data
from generators.ranking_generator import generate_ranking_data
from generators.prediction_generator import (generate_admission_predictions,
                                           generate_salary_predictions)
from generators.user_generator import generate_users
from generators.wishlist_generator import generate_wishlist
from generators.application_generator import generate_applications
from generators.value_analysis_generator import generate_value_analysis
from generators.combined_datasets import *

def save_to_csv(df, filename):
    """Save DataFrame to CSV with checks"""
    path = f'data/{filename}'
    if not os.path.exists(path):
        df.to_csv(path, index=False)
        print(f"Saved {filename} ({len(df)} records)")
    else:
        print(f"{filename} already exists - skipping")

def generate_if_not_exists(generator_func, filename, *args, **kwargs):
    """Generate data only if file doesn't exist"""
    path = f'data/{filename}'
    if not os.path.exists(path):
        print(f"Generating {filename}...")
        df = generator_func(*args, **kwargs)
        save_to_csv(df, filename)
        return df
    else:
        print(f"Loading existing {filename}...")
        return pd.read_csv(path)

def main():
    # Setup
    os.makedirs('data', exist_ok=True)
    initialize_generators(SEED)
    
    # Generate or load data
    universities = generate_if_not_exists(
        generate_universities, 'universities.csv'
    )
    
    students = generate_if_not_exists(
        generate_students, 'students.csv'
    )
    
    programs = generate_if_not_exists(
        generate_programs, 'programs.csv', universities
    )
    
    generate_if_not_exists(
        generate_admissions, 'admissions.csv', programs
    )
    
    generate_if_not_exists(
        generate_historical_admissions, 'historical_admissions.csv', 
        programs, students
    )
    
    generate_if_not_exists(
        generate_alumni_salary_data, 'alumni_salary.csv',
        programs, students
    )
    
    generate_if_not_exists(
        generate_funding_data, 'funding.csv', universities
    )
    
    generate_if_not_exists(
        generate_ranking_data, 'rankings.csv', programs
    )
    
    generate_if_not_exists(
        generate_admission_predictions, 'admission_predictions.csv',
        students, programs
    )
    
    generate_if_not_exists(
        generate_salary_predictions, 'salary_predictions.csv',
        students, programs
    )
    
    generate_if_not_exists(
        generate_users, 'users.csv', students
    )
    
    generate_if_not_exists(
        generate_wishlist, 'wishlist.csv', students, programs
    )
    
    generate_if_not_exists(
        generate_applications, 'applications.csv', students, programs
    )
    
    generate_if_not_exists(
        generate_value_analysis, 'value_analysis.csv', programs
    )

    # # Combine datasets
    # combined_path = 'combined/master_dataset.csv'
    # if not os.path.exists(combined_path):
    #     print("Combining datasets...")
    #     load_and_prepare()
    #     combine_efficiently()
    #     print(f"Master dataset created at {combined_path}")
    # else:
    #     print("Master dataset already exists - skipping combination")

if __name__ == "__main__":
    main()