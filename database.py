import sqlite3
from datetime import datetime

# Function to create/connect to SQLite database
def create_db():
    # Connect to SQLite database (it will create the database file if it doesn't exist)
    conn = sqlite3.connect('patient_data.db')
    c = conn.cursor()

    # Drop the patients table if it exists (so we can recreate it with the updated schema)
    c.execute('DROP TABLE IF EXISTS patients')
    
    # Create the patients table with the new schema (including visit_date)
    c.execute('''CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    age INTEGER,
                    gender TEXT,
                    contact_info TEXT,
                    symptoms TEXT,
                    predicted_disease TEXT,
                    visit_date TEXT
                )''')
    
    # Commit changes and close the connection
    conn.commit()
    conn.close()


# Function to insert patient data into the database (with visit_date)
def insert_patient_data(name, age, gender, contact_info, symptoms, predicted_disease, visit_date=None):
    if visit_date is None:
        visit_date = datetime.now().strftime('%Y-%m-%d')  # Default to current date if not provided

    conn = sqlite3.connect('patient_data.db')
    c = conn.cursor()

    # Insert the patient data into the table
    c.execute('''INSERT INTO patients (name, age, gender, contact_info, symptoms, predicted_disease, visit_date)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (name, age, gender, contact_info, ', '.join(symptoms), predicted_disease, visit_date))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Function to fetch patient data from the database (with visit_date)
def fetch_patient_data(name):
    conn = sqlite3.connect('patient_data.db')
    c = conn.cursor()

    # Fetch all records for a specific patient (filter by name)
    c.execute('SELECT * FROM patients WHERE name = ?', (name,))
    records = c.fetchall()

    conn.close()
    return records

# Example usage of the functions
create_db()  # This creates the table if it doesn't exist

# Inserting a sample patient's data with visit date
insert_patient_data(
    name="John Doe",
    age=30,
    gender="Male",
    contact_info="john.doe@example.com",
    symptoms=["fever", "cough", "fatigue"],
    predicted_disease="Flu",
    visit_date="2024-12-21"  # Optional; defaults to current date if not provided
)

# Fetching patient data (this could be used to display in the app)
patients = fetch_patient_data("John Doe")
for patient in patients:
    print(patient)  # Display patient data
