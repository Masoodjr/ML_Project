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

def save_to_csv(df, filename):
    df.to_csv(f'data/{filename}', index=False)

def main():
    # Setup
    os.makedirs('data', exist_ok=True)
    initialize_generators(SEED)
    
    # Generate data
    print("Generating universities...")
    universities = generate_universities()
    save_to_csv(universities, 'universities.csv')
    
    print("Generating students...")
    students = generate_students()
    save_to_csv(students, 'students.csv')
    
    print("Generating programs...")
    programs = generate_programs(universities)
    save_to_csv(programs, 'programs.csv')
    
    print("Generating admissions criteria...")
    admissions = generate_admissions(programs)
    save_to_csv(admissions, 'admissions.csv')
    
    print("Generating historical admissions...")
    historical_admissions = generate_historical_admissions(programs, students)
    save_to_csv(historical_admissions, 'historical_admissions.csv')
    
    print("Generating alumni salary data...")
    alumni_salary = generate_alumni_salary_data(programs, students)
    save_to_csv(alumni_salary, 'alumni_salary.csv')
    
    print("Generating funding data...")
    funding = generate_funding_data(universities)
    save_to_csv(funding, 'funding.csv')
    
    print("Generating ranking data...")
    rankings = generate_ranking_data(programs)
    save_to_csv(rankings, 'rankings.csv')
    
    print("Generating admission predictions...")
    admission_preds = generate_admission_predictions(students, programs)
    save_to_csv(admission_preds, 'admission_predictions.csv')
    
    print("Generating salary predictions...")
    salary_preds = generate_salary_predictions(students, programs)
    save_to_csv(salary_preds, 'salary_predictions.csv')
    
    print("Generating users...")
    users = generate_users(students)
    save_to_csv(users, 'users.csv')
    
    print("Generating wishlist...")
    wishlist = generate_wishlist(students, programs)
    save_to_csv(wishlist, 'wishlist.csv')
    
    print("Generating applications...")
    applications = generate_applications(students, programs)
    save_to_csv(applications, 'applications.csv')
    
    print("Data generation complete!")

if __name__ == "__main__":
    main()