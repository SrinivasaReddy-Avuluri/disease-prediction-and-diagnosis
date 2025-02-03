import sqlite3
import streamlit as st
import joblib
import numpy as np
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# Load the Random Forest model and Label Encoder
rf_model = joblib.load('random_forest_model.pkl')
le = joblib.load('label_encoder.pkl')

# Load the diet data
diet_df = pd.read_pickle('diet_data.pkl')

# Function to create/connect to SQLite database
def create_db():
    conn = sqlite3.connect('patient_data.db')
    c = conn.cursor()

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
    
    conn.commit()
    conn.close()

# Function to insert patient data into the database
def insert_patient_data(name, age, gender, contact_info, symptoms, predicted_disease):
    conn = sqlite3.connect('patient_data.db')
    c = conn.cursor()

    visit_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    c.execute('''INSERT INTO patients (name, age, gender, contact_info, symptoms, predicted_disease, visit_date)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (name, age, gender, contact_info, ', '.join(symptoms), predicted_disease, visit_date))

    conn.commit()
    conn.close()

# Function to fetch patient data from the database, sorted by the latest visit date
def fetch_patient_data(name):
    conn = sqlite3.connect('patient_data.db')
    c = conn.cursor()

    c.execute('SELECT * FROM patients WHERE name = ? ORDER BY visit_date DESC', (name,))
    records = c.fetchall()

    conn.close()
    return records

# Function to convert symptoms to binary array
def get_symptom_array(selected_symptoms, all_symptoms):
    symptom_array = [0] * len(all_symptoms)
    for symptom in selected_symptoms:
        if symptom in all_symptoms:
            symptom_index = all_symptoms.index(symptom)
            symptom_array[symptom_index] = 1
    return symptom_array

# Function to get diet and medication for predicted disease
def get_diet_for_disease(predicted_disease):
    disease_data = diet_df[diet_df['Disease'] == predicted_disease]
    if not disease_data.empty:
        suggested_diet = disease_data['Suggested Diet'].values[0]
        foods_to_eat = disease_data['Foods to Eat'].values[0]
        foods_to_avoid = disease_data['Foods to Avoid'].values[0]
        medication = disease_data['Medication'].values[0]
        additional_tips = disease_data['Additional Tips'].values[0] if 'Additional Tips' in disease_data.columns else "No additional tips available."
        return {
            'Disease': predicted_disease,
            'Suggested Diet': suggested_diet,
            'Foods to Eat': foods_to_eat,
            'Foods to Avoid': foods_to_avoid,
            'Medication': medication,
            'Additional Tips': additional_tips
        }
    else:
        return {"Error": "Disease not found in the dataset"}

# Full list of symptoms (133)
all_symptoms = [
    'itching', 'skin_rash', 'nodal_skin_eruptions', 'continuous_sneezing', 'shivering', 'chills', 'joint_pain',
    'stomach_pain', 'acidity', 'ulcers_on_tongue', 'muscle_wasting', 'vomiting', 'burning_micturition', 'spotting_urination',
    'fatigue', 'weight_gain', 'anxiety', 'cold_hands_and_feets', 'mood_swings', 'weight_loss', 'restlessness', 'lethargy',
    'patches_in_throat', 'irregular_sugar_level', 'cough', 'high_fever', 'sunken_eyes', 'breathlessness', 'sweating',
    'dehydration', 'indigestion', 'headache', 'yellowish_skin', 'dark_urine', 'nausea', 'loss_of_appetite', 'pain_behind_the_eyes',
    'back_pain', 'constipation', 'abdominal_pain', 'diarrhoea', 'mild_fever', 'yellow_urine', 'yellowing_of_eyes',
    'acute_liver_failure', 'fluid_overload', 'swelling_of_stomach', 'swelled_lymph_nodes', 'malaise',
    'blurred_and_distorted_vision', 'phlegm', 'throat_irritation', 'redness_of_eyes', 'sinus_pressure', 'runny_nose', 'congestion',
    'chest_pain', 'weakness_in_limbs', 'fast_heart_rate', 'pain_during_bowel_movements', 'pain_in_anal_region', 'bloody_stool',
    'irritation_in_anus', 'neck_pain', 'dizziness', 'cramps', 'bruising', 'obesity', 'swollen_legs', 'swollen_blood_vessels',
    'puffy_face_and_eyes', 'enlarged_thyroid', 'brittle_nails', 'swollen_extremeties', 'excessive_hunger', 'extra_marital_contacts',
    'drying_and_tingling_lips', 'slurred_speech', 'knee_pain', 'hip_joint_pain', 'muscle_weakness', 'stiff_neck', 'swelling_joints',
    'movement_stiffness', 'spinning_movements', 'loss_of_balance', 'unsteadiness', 'weakness_of_one_body_side', 'loss_of_smell',
    'bladder_discomfort', 'foul_smell_of_urine', 'continuous_feel_of_urine', 'passage_of_gases', 'internal_itching', 'toxic_look_(typhos)',
    'depression', 'irritability', 'muscle_pain', 'altered_sensorium', 'red_spots_over_body', 'belly_pain', 'abnormal_menstruation',
    'dischromic _patches', 'watering_from_eyes', 'increased_appetite', 'polyuria', 'family_history', 'mucoid_sputum', 'rusty_sputum',
    'lack_of_concentration', 'visual_disturbances', 'receiving_blood_transfusion', 'receiving_unsterile_injections', 'coma',
    'stomach_bleeding', 'distention_of_abdomen', 'history_of_alcohol_consumption', 'fluid_overload.1', 'blood_in_sputum',
    'prominent_veins_on_calf', 'palpitations', 'painful_walking', 'pus_filled_pimples', 'blackheads', 'scurring', 'skin_peeling',
    'silver_like_dusting', 'small_dents_in_nails', 'inflammatory_nails', 'blister', 'red_sore_around_nose', 'yellow_crust_ooze'
]

# Function to create PDF with patient details and disease prediction
def create_pdf(patient_data, disease_info):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Patient Report", ln=True, align='C')

    # Add patient details to PDF
    for key, value in patient_data.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True, align='L')

    # Add predicted disease and diet details
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Predicted Disease: {disease_info['Disease']}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Suggested Diet: {disease_info['Suggested Diet']}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Foods to Eat: {disease_info['Foods to Eat']}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Foods to Avoid: {disease_info['Foods to Avoid']}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Medication: {disease_info['Medication']}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Additional Tips: {disease_info['Additional Tips']}", ln=True, align='L')

    # Save PDF to file
    pdf_file_path = "patient_report.pdf"
    pdf.output(pdf_file_path)
    return pdf_file_path

# Streamlit Interface
st.title("Disease Prediction & Patient History")
st.sidebar.header("Patient Details")

# Input Fields
name = st.text_input("Name")
age = st.number_input("Age", min_value=1)
gender = st.selectbox("Gender", ["Male", "Female", "Other"])
contact_info = st.text_input("Contact Information")
selected_symptoms = st.multiselect("Select Symptoms", all_symptoms)

# Predict disease when symptoms are selected
if age < 1:
    st.warning("Please ensure that the age is 1 or greater.")
else:
    # Predict Disease Button
    if st.button('Predict Disease'):
        if len(selected_symptoms) < 3:
            st.warning("Please select at least 3 symptoms for a valid prediction.")
            st.info("Selecting more symptoms improves the accuracy of the prediction.")
        else:
            # Convert selected symptoms to binary array
            input_data = get_symptom_array(selected_symptoms, all_symptoms)
            input_data = np.array(input_data).reshape(1, -1)

            # Predict disease
            disease_prediction = rf_model.predict(input_data)
            predicted_disease = le.inverse_transform(disease_prediction)[0]

            # Get diet, medication, and drug details
            disease_info = get_diet_for_disease(predicted_disease)

            # Display prediction results
            st.subheader(f"Predicted Disease: {predicted_disease}")

            if 'Error' in disease_info:
                st.error(disease_info['Error'])
            else:
                st.write(f"**Suggested Diet**: {disease_info['Suggested Diet']}")
                st.write(f"**Foods to Eat**: {disease_info['Foods to Eat']}")
                st.write(f"**Foods to Avoid**: {disease_info['Foods to Avoid']}")
                st.write(f"**Medication**: {disease_info['Medication']}")
                st.write(f"**Additional Tips**: {disease_info['Additional Tips']}")

            # Save data to database
            insert_patient_data(name, age, gender, contact_info, selected_symptoms, predicted_disease)

            # Generate and download PDF
            patient_data = {
                "Name": name,
                "Age": age,
                "Gender": gender,
                "Contact Info": contact_info,
                "Symptoms": ', '.join(selected_symptoms)
            }

            pdf_file_path = create_pdf(patient_data, disease_info)
            st.download_button("Download Report", data=open(pdf_file_path, 'rb'), file_name="patient_report.pdf", mime="application/pdf")

    # Patient history (optional)
    st.sidebar.subheader("Patient History")
    search_name = st.text_input("Enter Name to Search Patient History")

    if search_name:
        patient_history = fetch_patient_data(name)

        # Display Patient History in Table
        if patient_history:
            df = pd.DataFrame(patient_history, columns=["ID", "Name", "Age", "Gender", "Contact Info", "Symptoms", "Predicted Disease", "Visit Date"])
            st.table(df)
        else:
            st.warning(f"No records found for {search_name}")