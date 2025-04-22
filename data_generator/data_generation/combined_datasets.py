import pandas as pd
import os
from tqdm import tqdm  # For progress bars

def load_and_prepare(data_dir='data'):
    """Load datasets with memory-efficient dtypes"""
    print("Loading datasets...")
    dfs = {}
    
    # Load with optimized dtypes
    dfs['students'] = pd.read_csv(f'{data_dir}/students.csv', 
                                dtype={'student_id': 'int32',
                                      'gre_score': 'float32',
                                      'gpa': 'float32'})
    
    dfs['programs'] = pd.read_csv(f'{data_dir}/programs.csv',
                                dtype={'program_id': 'int32',
                                      'university_id': 'int32'})
    
    dfs['universities'] = pd.read_csv(f'{data_dir}/universities.csv',
                                    dtype={'university_id': 'int32'})
    
    # Only load necessary columns from large tables
    student_relations = {
        'wishlist': ['student_id', 'program_id', 'priority'],
        'applications': ['student_id', 'program_id', 'status'],
        'admission_predictions': ['student_id', 'program_id', 'admission_probability'],
        'salary_predictions': ['student_id', 'program_id', 'predicted_salary']
    }
    
    for table, cols in student_relations.items():
        dfs[table] = pd.read_csv(f'{data_dir}/{table}.csv', 
                                usecols=cols,
                                dtype={'student_id': 'int32',
                                      'program_id': 'int32'})
    
    return dfs

def combine_efficiently(data_dir='data', chunk_size=100000):
    """Combine datasets with memory efficiency"""
    dfs = load_and_prepare(data_dir)
    
    print("Merging student data...")
    # Start with students
    combined = dfs['students']
    
    # Merge student-related tables
    student_tables = ['wishlist', 'applications', 
                    'admission_predictions', 'salary_predictions']
    
    for table in tqdm(student_tables):
        if table in dfs:
            combined = combined.merge(
                dfs[table],
                on='student_id',
                how='left',
                suffixes=('', f'_{table}')
            )
    
    print("Adding program info...")
    # Merge program info in chunks if large
    if len(combined) > chunk_size:
        chunks = [combined.iloc[i:i + chunk_size] for i in range(0, len(combined), chunk_size)]
        merged_chunks = []
        
        for chunk in tqdm(chunks):
            merged = chunk.merge(
                dfs['programs'],
                on='program_id',
                how='left'
            )
            merged_chunks.append(merged)
        
        combined = pd.concat(merged_chunks)
    else:
        combined = combined.merge(
            dfs['programs'],
            on='program_id',
            how='left'
        )
    
    print("Adding university info...")
    combined = combined.merge(
        dfs['universities'],
        on='university_id',
        how='left',
        suffixes=('', '_univ')
    )
    
    print("Finalizing...")
    # Clean up
    combined = combined.loc[:, ~combined.columns.duplicated()]
    
    # Save
    os.makedirs('combined', exist_ok=True)
    output_path = f'combined/master_dataset_optimized.csv'
    
    # Save in chunks if too large
    if len(combined) > chunk_size:
        for i in tqdm(range(0, len(combined), chunk_size)):
            chunk = combined.iloc[i:i + chunk_size]
            mode = 'w' if i == 0 else 'a'
            header = i == 0
            chunk.to_csv(output_path, mode=mode, header=header, index=False)
    else:
        combined.to_csv(output_path, index=False)
    
    print(f"Optimized combined dataset saved to {output_path}")
    print(f"Final shape: {combined.shape}")

if __name__ == "__main__":
    combine_efficiently()