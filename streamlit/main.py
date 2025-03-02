import streamlit as st
import pandas as pd
import requests
import base64
import os
from PIL import Image

# FastAPI Ngrok URL
API_URL = 'https://d4fc-182-3-53-232.ngrok-free.app'

# App Config
st.set_page_config(page_title="Ascencio Course Selection", page_icon="🧩", layout="wide")
img = Image.open("streamlit/bg.png")

# Custom CSS for better appearance
st.markdown("""
<style>
    .main-header {
        text-align: right;
        margin-bottom: 18px;
        font-size: 30px !important;
        font-weight: bold;
    }
    .main-header-2 {
        text-align: center;
        margin-bottom: 18px;
        font-size: 20px !important;
        font-weight: bold;
    }
    .sub-title {
        text-align: center;
        margin-bottom: 20px;
    }
    .sub-title-2 {
        font-size: 20px !important;
        text-align: center;
        font-weight: normal !important;
    }
</style>
""", unsafe_allow_html=True)

# Function
## Check API Status
def check_api_connection():
    try:
        response = requests.get(f'{API_URL}/')
        return response.status_code == 200
    except:
        return False

## Download Excel Template
def download_excel_template():
    try:
        response = requests.get(f'{API_URL}/create_excel_template')
        if response.status_code == 200:
            return response.content
        else:
            return None
    except:
        return None

## Mapping Features
def single_mapping(input_data):
    # last_new_job
    if input_data["last_new_job"] == "More than 4":
        input_data["last_new_job"] = ">4"
    elif input_data["last_new_job"] == "Never":
        input_data["last_new_job"] = "never"
    # experience
    input_data["experience"] = str(input_data['experience'])
    if input_data["experience"] == "0":
        input_data["experience"] = "<1"
    elif input_data["experience"] == "21":
        input_data["experience"] = ">20"
    # company_size
    if input_data["company_size"] == "Less than 10":
        input_data["company_size"] = "<10"
    elif input_data["company_size"] == "10 to 49":
        input_data["company_size"] = "10-49"
    elif input_data["company_size"] == "50 to 99":
        input_data["company_size"] = "50-99"
    elif input_data["company_size"] == "100 to 499":
        input_data["company_size"] = "100-500"
    elif input_data["company_size"] == "500 to 999":
        input_data["company_size"] = "500-999"
    elif input_data["company_size"] == "1000 to 4999":
        input_data["company_size"] = "1000-4999"
    elif input_data["company_size"] == "5000 to 9999":
        input_data["company_size"] = "5000-9999"
    elif input_data["company_size"] == "More than 9999":
        input_data["company_size"] = "10000+"
    # relevant_experience
    if input_data["relevant_experience"] == "Yes":
        input_data["relevant_experience"] = True
    else:
        input_data["relevant_experience"] = False
    return input_data

## Process Excel File
def mass_mapping(uploaded_file):
    try:
        # Read excel file
        df = pd.read_excel(uploaded_file)
        # Check required columns
        required_columns = [
            'Full Name', 'Gender', 'Enrolled University', 'Work Experience', 
            'Data Science Experience', 'Duration of Last New Job', 'Education Level', 
            'Major Discipline', 'City Development Index', 'Company Size', 'Company Type'
        ]
        for column in required_columns:
            if column not in df.columns:
                return {"status": "error", "message": f"Missing required column: {column}"}
        # Drop NA
        shape_old = df.shape[0]
        df = df.dropna()
        shape_new = df.shape[0]
        if shape_old != shape_new:
            return {"status": "error", "message": "There are missing values in the dataset"}
        # Map column names
        column_mapping = {
            'Full Name': 'full_name',
            'Gender': 'gender',
            'Enrolled University': 'enrolled_university',
            'Work Experience': 'experience',
            'Data Science Experience': 'relevant_experience',
            'Duration of Last New Job': 'last_new_job',
            'Education Level': 'education_level',
            'Major Discipline': 'major_discipline',
            'City Development Index': 'city_development_index',
            'Company Size': 'company_size',
            'Company Type': 'company_type'
        }
        df = df.rename(columns=column_mapping)
        # Map values
        # last_new_job
        df['last_new_job'] = df['last_new_job'].astype(str)
        df['last_new_job'] = df['last_new_job'].apply(lambda x: ">4" if x == "More than 4" else ("never" if x == "Never" else x))
        # experience
        df['experience'] = df['experience'].astype(str)
        df['experience'] = df['experience'].apply(lambda x: "<1" if x == "0" else (">20" if x == "21" else x))
        # company_size
        company_size_mapping = {
            'Less than 10': '<10',
            '10 to 49': '10-49',
            '50 to 99': '50-99',
            '100 to 499': '100-500',
            '500 to 999': '500-999',
            '1000 to 4999': '1000-4999',
            '5000 to 9999': '5000-9999',
            'More than 9999': '10000+'
        }
        df['company_size'] = df['company_size'].map(company_size_mapping)
        # relevant_experience
        relevant_experience_mapping = {
            'Yes': True,
            'No': False
        }
        df['relevant_experience'] = df['relevant_experience'].map(relevant_experience_mapping)
        # Order columns by alphabet
        df = df[[
            'city_development_index', 'company_size', 'company_type', 'education_level', 'enrolled_university', 'experience', 'full_name', 'gender', 'last_new_job', 'major_discipline', 'relevant_experience'
        ]]
        # Convert to JSON
        records = df.to_dict('records')
        return records
    except Exception as e:
        return {"status": "error", "message": str(e)}

## Process Multiple Employees Data
def preprocess_and_predict(employee_data,mass=False):
    try:
        # Preprocess
        if mass:
            preprocess_response = requests.post(
                f'{API_URL}/preprocess', 
                json={"employees": employee_data}
                )
        else:
            preprocess_response = requests.post(
                f'{API_URL}/preprocess', 
                json={"employees": [employee_data]}
                )
        if preprocess_response.status_code != 200:
            return {"status": "error", "message": preprocess_response.json()}
        # Predict
        predict_response = requests.post(
            f'{API_URL}/predict', 
            json=preprocess_response.json()
            )
        if predict_response.status_code != 200:
            return {"status": "error", "message": "Failed to predict data"}
        # Output      
        return predict_response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

## Session State Management
def initialize_session_state():
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'prediction_results' not in st.session_state:
        st.session_state.prediction_results = None

## Navigation
def navigate_to(page):
    st.session_state.page = page

## UI Component
### Header
def display_header():
    col1, col2, col3, col4, col5 = st.columns([1, 1, 5, 5, 5], vertical_alignment='center')
    with col1:
        st.button("Home", key='home', on_click=navigate_to, args=('landing',), use_container_width=True)
    with col2:
        st.button("About", key='about', on_click=navigate_to, args=('about',), use_container_width=True)
    with col5:
        st.markdown('<p class="main-header">🧩 Ascencio Course Selection</p>', unsafe_allow_html=True)

### Download Excel Button
def download_button(content, filename, button_text):
    b64 = base64.b64encode(content).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">{button_text}</a>'
    return href

# Pages
def landing_page():
    display_header()
    # Add image
    st.markdown("")
    col1, col2, col3 = st.columns(3)
    with col2:
        st.image(img, use_container_width=True)
    # Add button
    col1, col2, col3, col4 = st.columns(4)
    with col2:
        st.button("Single Prediction", key='single_pred', on_click=navigate_to, args=('single_input',), use_container_width=True)
    with col3:
        st.button("Mass Prediction", key='mass_pred', on_click=navigate_to, args=('mass_input',), use_container_width=True)
    # Add API Checking
    st.markdown("")
    if not check_api_connection():
        st.error("❌ Cannot connect to prediction API. Please check your backend server.")

def about_page():
    display_header()
    # Add description
    st.markdown("""
    # HR Analytics - Job Change of Data Scientists

    > Data from [Kaggle](https://www.kaggle.com/datasets/arashnic/hr-analytics-job-change-of-data-scientists) with modification in problem context.

    _This project was completed as a part of Rakamin Academy Data Science Bootcamp._

    Ascencio, a leading Data Science agency, offers training courses to companies to enhance their employees' skills. Companies want to predict which employees are **unlikely to seek a job change** after completing the course. By focusing on employees who are committed to staying and can contribute sooner, Ascencio helps companies optimize their training investments.

    In this project, companies can input single or multiple employee data to predict which employees are **unlikely or likely to seek a job change** after completing the course. After prediction, companies can consult with AI Chatbot about the result for additional discussion.

    ----

    > We open about further discusion and you can contact us via LinkedIn or check our GitHub repository.
    """)
    # Add photo profile
    st.markdown("")
    col1, col2, col3 = st.columns(3,border=True)
    with col1:
        st.image(img, use_container_width=True)
    with col2:
        st.image(img, use_container_width=True)
    with col3:
        st.image(img, use_container_width=True)
    # Add name and contact
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <p class="main-header-2">
        Muhammad Naufal At-Thoriq
        </p>
        """, unsafe_allow_html=True)
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            st.link_button("LinkedIn", "https://www.linkedin.com/in/mnatthoriq/", use_container_width=True)
        with sub_col2:
            st.link_button("GitHub", "https://github.com/MN-Atthoriq", use_container_width=True)
    with col2:
        st.markdown("""
        <p class="main-header-2">
        Muhammad Naufal At-Thoriq
        </p>
        """, unsafe_allow_html=True)
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            st.link_button("LinkedIn", "https://www.linkedin.com/in/mnatthoriq/", use_container_width=True)
        with sub_col2:
            st.link_button("GitHub", "https://github.com/MN-Atthoriq", use_container_width=True)
    with col3:
        st.markdown("""
        <p class="main-header-2">
        Muhammad Naufal At-Thoriq
        </p>
        """, unsafe_allow_html=True)
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            st.link_button("LinkedIn", "https://www.linkedin.com/in/mnatthoriq/", use_container_width=True)
        with sub_col2:
            st.link_button("GitHub", "https://github.com/MN-Atthoriq", use_container_width=True)

def single_input_page():
    display_header()
    check = False # for checking if need to show button for navigate
    st.markdown('<h2 class="sub-title">SINGLE EMPLOYEE PREDICTION</h2>', unsafe_allow_html=True)
    with st.form('single_input_form'):
        full_name = st.text_input("Full Name", help="Enter the full name of the employee.", max_chars=200)
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox("Gender", help="Select the gender of the employee.", 
                                    options=["Male", "Female", "Other"])
            enrolled_university = st.selectbox("Enrolled University", help="Specify whether the employee is curently enroll in a university.", 
                                                options=["No Enroll", "Part Time", "Full Time"])
            experience = st.number_input("Work Experience", help="Enter the total years of employee’s work experience. If more than 20 years, input ’21’.",
                                        min_value=0, max_value=21, value=0, step=1)
            relevant_experience = st.selectbox("Data Science Experience", help="Specify if employee have relevant experience in data science.",
                                                options=["Yes", "No"])
            last_new_job = st.selectbox("Duration of Last New Job", help="Enter the duration (in years) since the employee’s last new job.", 
                                       options=["Never", "1", "2", "3", "4", "More than 4"]) 
        with col2:
            education_level = st.selectbox("Education Level", help="Specify the highest education level achieved by the employee.",
                                          options=["Primary School", "High School", "Graduate", "Masters", "Phd"])
            major_discipline = st.selectbox("Major Discipline", help="Specify the major discipline of the employee’s highest qualification. If the employee’s highest education level is High School or lower, input ’No Major’.",
                                           options=["STEM", "Humanities", "Business Degree", "Arts", "No Major", "Other"])
            city_development_index = st.slider("City Development Index", help="Input the City Development Index (a metric representing the level of urban development) for the location where the company is based.",
                                                min_value=0.0, max_value=1.0, value=0.5, step=0.01)
            company_size = st.selectbox("Company Size", help="Specify the size of the company based on the number of employees.",
                                       options=["Less than 10","10 to 49","50 to 99","100 to 499","500 to 999","1000 to 4999","5000 to 9999","More than 9999"])
            company_type = st.selectbox("Company Type", help="Enter the type of company.",
                                       options=["Pvt Ltd", "Public Sector", "Funded Startup", "Early Startup", "NGO", "Other"])
        submitted = st.form_submit_button("Submit")
        if submitted:
            if not full_name or not gender or not enrolled_university or experience is None or not relevant_experience or not last_new_job or not education_level or not major_discipline or city_development_index is None or not company_size or not company_type:
                st.error("Please fill in all the fields.")
            else:
                with st.spinner("Processing..."):
                    input_data = {
                        'city_development_index': city_development_index,
                        'company_size': company_size,
                        'company_type': company_type,
                        'education_level': education_level,
                        'enrolled_university': enrolled_university,
                        'experience': experience,
                        'full_name': full_name,
                        'gender': gender,
                        'last_new_job': last_new_job,
                        'major_discipline': major_discipline,
                        'relevant_experience': relevant_experience
                    }
                    employee_data = single_mapping(input_data)
                    result = preprocess_and_predict(employee_data)
                    if result.get('status') == 'error':
                        st.error(f"Error: {result.get('message')}")
                    else:
                        st.session_state.prediction_results = result
                        check = True
    if check:
        st.button("Navigate to Prediction Results", key='single_pred', on_click=navigate_to, args=('prediction_results',))

def mass_input_page():
    display_header()
    check = False
    st.markdown('<h2 class="sub-title">MASS EMPLOYEE PREDICTION</h2>', unsafe_allow_html=True)
    st.markdown('<br><br><br>', unsafe_allow_html=True)
    # Download template button
    template_data = download_excel_template()
    col1, col2, col3 = st.columns(3)
    with col2:
        with st.expander("Tutorial How to Use Mass Employee Prediction"):
            st.markdown("""
            1. Download the template
            2. Fill in the data. Maximum 1000 employees for each predictions
            3. Upload the completed template
            """)
        st.markdown('<br>', unsafe_allow_html=True)
        if template_data:
            st.download_button(
                label="📥 Download Excel Template",
                data=template_data,
                file_name="mass_employee_input.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.warning("Could not retrieve the template. Please check your API connection.")
        # Upload file
        uploaded_file = st.file_uploader("Upload Completed Template", type=["xlsx"], label_visibility="hidden")
        if uploaded_file:
            with st.spinner("Processing..."):
                employee_data = mass_mapping(uploaded_file)
                result = preprocess_and_predict(employee_data,mass=True)
                if result.get('status') == 'error':
                    st.error(f"Error: {result.get('message')}")
                else:
                    st.session_state.prediction_results = result
                    check = True
                    st.markdown('<br>', unsafe_allow_html=True)
        if check:
            st.button("Navigate to Prediction Results", key='mass_pred', on_click=navigate_to, args=('prediction_results',), use_container_width=True)
    

def prediction_results_page():
    display_header()
    # st.markdown('<h2 class="sub-title">Prediction Results</h2>', unsafe_allow_html=True)
    
    # if st.session_state.prediction_results is None:
    #     st.warning("No prediction results available.")
    #     return
    
    # results = st.session_state.prediction_results.get("results", [])
    
    # st.write(f"Total predictions: {len(results)}")
    
    # for i, result in enumerate(results):
    #     original_data = result.get("original_data", {})
    #     prediction = result.get("prediction", 0)
    #     probability = result.get("probability", 0)
        
    #     prediction_class = "positive-prediction" if prediction == 1 else "negative-prediction"
        
    #     st.markdown(f"""
    #     <div class="prediction-card {prediction_class}">
    #         <h3>{original_data.get('full_name', f'Employee {i+1}')}</h3>
    #         <p><strong>Prediction:</strong> {"Likely to change job" if prediction == 1 else "Likely to stay"}</p>
    #         <p><strong>Probability:</strong> {probability:.2%}</p>
    #         <details>
    #             <summary>Employee Details</summary>
    #             <ul>
    #                 <li><strong>Gender:</strong> {original_data.get('gender', 'N/A')}</li>
    #                 <li><strong>Education:</strong> {original_data.get('education_level', 'N/A')}</li>
    #                 <li><strong>Major:</strong> {original_data.get('major_discipline', 'N/A')}</li>
    #                 <li><strong>Experience:</strong> {original_data.get('experience', 'N/A')} years</li>
    #                 <li><strong>Relevant Experience:</strong> {'Yes' if original_data.get('relevant_experience', False) else 'No'}</li>
    #                 <li><strong>Enrolled University:</strong> {original_data.get('enrolled_university', 'N/A')}</li>
    #                 <li><strong>Company Size:</strong> {original_data.get('company_size', 'N/A')}</li>
    #                 <li><strong>Company Type:</strong> {original_data.get('company_type', 'N/A')}</li>
    #                 <li><strong>City Development Index:</strong> {original_data.get('city_development_index', 'N/A')}</li>
    #                 <li><strong>Last New Job:</strong> {original_data.get('last_new_job', 'N/A')}</li>
    #             </ul>
    #         </details>
    #     </div>
    #     """, unsafe_allow_html=True)
    
    # # Navigation buttons
    # col1, col2 = st.columns(2)
    
    # with col1:
    #     st.button("New Single Prediction", on_click=navigate_to, args=('single_input',), use_container_width=True)
    
    # with col2:
    #     st.button("New Bulk Prediction", on_click=navigate_to, args=('mass_input',), use_container_width=True)
    
    # # Placeholder for future chatbot button
    # st.markdown("---")
    # st.info("💬 Coming Soon: AI Assistant to help you understand these predictions!")

# Main
def main():
    initialize_session_state()
    if st.session_state.page == 'landing':
        landing_page()
    elif st.session_state.page == 'about':
        about_page()
    elif st.session_state.page == 'single_input':
        single_input_page()
    elif st.session_state.page == 'mass_input':
        mass_input_page()
    elif st.session_state.page == 'prediction_results':
        prediction_results_page()

if __name__ == '__main__':
    main()