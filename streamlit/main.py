import streamlit as st
import pandas as pd
import requests
import base64
import os
from PIL import Image

# FastAPI Ngrok URL
API_URL = st.secrets("FASTAPI_NGROK_URL") # Replace with your FastAPI Ngrok URL

# App Config
st.set_page_config(page_title="Ascencio Course Selection", page_icon="🧩", layout="wide")
img = Image.open("bg.png")
img_renato = Image.open("renato.png")
img_naufal = Image.open("naufal.png")

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
    .sub-title-3 {
        font-size: 20px !important;
        text-align: left;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# Function
## Check API Status
def check_api_connection():
    """
    Check if the FastAPI application is running and can be connected

    Returns
    ------- 
    bool
        A boolean indicating the status of the API connection
    """
    try:
        response = requests.get(f'{API_URL}/')
        return response.status_code == 200
    except:
        return False

## Download Excel Template
def download_excel_template():
    """
    Download the Excel template from the FastAPI application for mass input

    Returns
    -------
    bytes
        The content of the Excel template if the API connection is successful, None otherwise
    """
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
    """
    Map the input data to the correct format for the FastAPI application.

    Parameters
    ----------
    input_data : dict
        A dictionary containing the input data

    Returns
    -------
    dict
        A dictionary containing the mapped input data
    """
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
    """
    Process an Excel file containing mass input data.

    Parameters
    ----------
    uploaded_file : file
        The Excel file containing the mass input data

    Returns
    -------
    dict or list
        A dictionary containing the error message if there is an error, or a list of dictionaries containing the mapped input data
    """
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
    """
    Preprocesses the employee data and predicts the likelihood of a job change.

    Parameters
    ----------
    employee_data : dict or list
        A dictionary or list of dictionaries containing employee data to be preprocessed.
    mass : bool, optional
        A boolean indicating whether to process multiple employees at once (default is False).

    Returns
    -------
    dict
        A dictionary containing the prediction results or an error message.
    """
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

## Ask LLM AI
def ask_ai(request,df_dict):
    """
    Ask AI a question based on employee data

    Parameters
    ----------
    request : str
        The question to ask the AI
    df_dict : dict
        A dictionary containing the results dataframe

    Returns
    -------
    dict
        A dictionary containing the AI's response or an error message
    """
    try:
        # API request payload
        payload = {
            "question": request,
            "df_dict": df_dict
        }
        ai_response = requests.post(
            f'{API_URL}/ai_ask', 
            json=payload
            )
        if ai_response.status_code != 200:
            return {"status": "error", "message": "Failed to ask AI"}
        return ai_response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}


## Session State Management
def initialize_session_state():
    """Initialize state variables if they do not exist.

    This function is meant to be called at the beginning of the app's execution.
    It checks if the state variables for the current page and prediction results
    exist and creates them if they don't. This is necessary because Streamlit's
    session state is not initialized until the first widget is rendered.

    """
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'prediction_results' not in st.session_state:
        st.session_state.prediction_results = None
    if 'dataframe_results' not in st.session_state:
        st.session_state.dataframe_results = None

## Navigation
def navigate_to(page):
    """
    Navigate to a specified page.

    This function updates the session state to set the current page to the 
    specified page. It is used to control the navigation within the application.

    Args:
        page (str): The name of the page to navigate to.
    """
    st.session_state.page = page

## UI Component
### Header
def display_header():
    """
    Display the header of the application.

    This function displays the header of the application which includes the
    navigation buttons to the landing page and the about page and the title of the
    application.

    The header is displayed using Streamlit columns. The navigation buttons are
    placed in the first two columns and the title of the application is placed in
    the last column. The title is displayed using a Streamlit markdown widget with
    a custom CSS class to style the text as a header.

    """
    col1, col2, col3, col4, col5 = st.columns([1, 1, 5, 5, 5], vertical_alignment='center')
    with col1: # Back to home
        st.button("Home", key='home', on_click=navigate_to, args=('landing',), use_container_width=True)
    with col2: # Go to about
        st.button("About", key='about', on_click=navigate_to, args=('about',), use_container_width=True)
    with col5: # Logo
        st.markdown('<p class="main-header">🧩 Ascencio Course Selection</p>', unsafe_allow_html=True)

### Download Excel Button
def download_button(content, filename, button_text):
    """
    Generates a download link for a given content.

    This function encodes the provided content in base64 and creates an HTML
    anchor tag that allows users to download the content as an Excel file 
    when clicked.

    Parameters
    ----------
    content : bytes
        The binary content of the file to be downloaded.
    filename : str
        The name of the file that will be used for the downloaded file.
    button_text : str
        The text to be displayed on the download link/button.

    Returns
    -------
    str
        An HTML anchor tag string that can be rendered in a Streamlit app to
        provide a download link for the specified content.
    """
    b64 = base64.b64encode(content).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">{button_text}</a>'
    return href

# Pages
def landing_page():
    """
    Display the landing page of the application.
    """
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
    """
    Display the about page of the application.

    The about page displays a description of the project, including the problem
    context, the objective, and the features of the application. The page also
    displays a photo profile of the authors and their contact information.

    """
    display_header()
    # Add description
    st.markdown("""
    # HR Analytics - Job Change of Data Scientists

    > Data from [Kaggle](https://www.kaggle.com/datasets/arashnic/hr-analytics-job-change-of-data-scientists) with modification in problem context.

    _This project was completed as a part of Rakamin Academy Data Science Bootcamp._

    Ascencio, a leading Data Science agency, offers training courses to companies to enhance their employees' skills. Companies want to predict which employees are **unlikely to seek a job change** after completing the course. By focusing on employees who are committed to staying and can contribute sooner, Ascencio helps companies optimize their training investments.

    In this project, companies can input single or multiple employee data to predict which employees are **unlikely or likely to seek a job change** after completing the course. After prediction, companies can consult with AI about the result for additional discussion.

    ----

    > We open about further discusion and you can contact us via LinkedIn or check our GitHub repository.
    """)
    # Add photo profile
    st.markdown("")
    col1, col2, col3, col4 = st.columns(4, gap='large')
    with col2:
        st.image(img_naufal, use_container_width=True)
    with col3:
        st.image(img_renato, use_container_width=True)
    # Add name and contact
    col1, col2, col3, col4 = st.columns(4, gap='large')
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
        Daniel Renato Marlen
        </p>
        """, unsafe_allow_html=True)
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            st.link_button("LinkedIn", "https://www.linkedin.com/in/daniel-renato-marlen-389739216", use_container_width=True)
        with sub_col2:
            st.link_button("GitHub", "https://github.com/platinum21asl", use_container_width=True)

def single_input_page():
    """
    Display the single employee prediction input page.

    This function renders a form where users can input information about a single
    employee to predict their likelihood of seeking a job change. The form collects
    various details such as the employee's full name, gender, education level, 
    experience, and company-related information. Upon submission, the input data is
    validated and processed for prediction. If successful, the prediction results
    are stored in the session state, and an option to navigate to the prediction 
    results page is provided.

    An error message is displayed if any field is left incomplete. A loading spinner
    is shown while processing the data for prediction.
    """
    display_header()
    check = False # for checking if need to show button for navigate
    st.markdown('<h2 class="sub-title">SINGLE EMPLOYEE PREDICTION</h2>', unsafe_allow_html=True)
    # Form for input
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
            # Validate input
            if not full_name or not gender or not enrolled_university or experience is None or not relevant_experience or not last_new_job or not education_level or not major_discipline or city_development_index is None or not company_size or not company_type:
                st.error("Please fill in all the fields.")
            else: # Preprocess and predict
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
                        check = True # show button
    if check:
        st.button("Navigate to Prediction Results", key='single_pred', on_click=navigate_to, args=('prediction_results',))

def mass_input_page():
    """
    Display the mass employee prediction page of the application.

    This function displays the mass employee prediction page, which allows users 
    to download an Excel template, fill in employee data, and upload the 
    completed template for batch prediction processing. The page includes 
    instructions and a download button for the template. Once the template is 
    uploaded, the data is preprocessed and predictions are made. If successful, 
    the user can navigate to the prediction results page.

    The template supports up to 50 employees per prediction. The function 
    ensures that all necessary fields are provided and handles errors if the 
    template cannot be retrieved or if prediction processing fails.

    """
    display_header()
    check = False # for checking if need to show button for navigate
    st.markdown('<h2 class="sub-title">MASS EMPLOYEE PREDICTION</h2>', unsafe_allow_html=True)
    st.markdown('<br><br><br>', unsafe_allow_html=True)
    # Download template button
    template_data = download_excel_template()
    col1, col2, col3 = st.columns(3)
    with col2:
        # Instructions
        with st.expander("Tutorial How to Use Mass Employee Prediction"):
            st.markdown("""
            1. Download the template
            2. Fill in the data. Maximum 50 employees for each predictions
            3. Upload the completed template
            """)
        st.markdown('<br>', unsafe_allow_html=True)
        if template_data:
            # Download button
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
                    check = True # show button
                    st.markdown('<br>', unsafe_allow_html=True)
        if check:
            st.button("Navigate to Prediction Results", key='mass_pred', on_click=navigate_to, args=('prediction_results',), use_container_width=True)
    

def prediction_results_page():
    """
    Display the prediction results page.

    This function renders the prediction results page, which displays the 
    results of employee predictions. It includes a header, a section for 
    searching predictions by employee full name, and a data table showing 
    all prediction results. The function also provides options for navigating 
    to new single or mass prediction input pages.

    If no prediction results are available in the session state, a warning 
    message is displayed. The prediction results include details such as 
    the employee's full name, gender, education level, company type, 
    probability of leaving, and prediction outcome (Leave or Stay). The 
    function uses conditional styling to highlight the risk level of 
    employees potentially leaving the company.
    """
    display_header()
    st.markdown('<h2 class="sub-title">Prediction Results</h2>', unsafe_allow_html=True)
    
    # Check if prediction results are available
    if st.session_state.prediction_results is None:
        st.warning("No prediction results available.")
        return
    
    # Make dataframe
    results = st.session_state.prediction_results.get("results", [])
    results_data = []
    for result in results:
        original_data = result.get("original_data", {})
        prediction = result.get("prediction", "N/A")
        probability = result.get("probability", "N/A")
        result_dict = {
            "Full Name": original_data.get("full_name", "N/A"),
            "Gender": original_data.get("gender", "N/A"),
            "Enrolled University": original_data.get("enrolled_university", "N/A"),
            "Work Experience": original_data.get("experience", "N/A"),
            "Data Science Experience": "Yes" if original_data.get("relevant_experience", "N/A") else "No",
            "Duration of Last New Job": "Never" if original_data.get("last_new_job", "N/A") == "never" 
                                        else "More than 4 years" if original_data.get("last_new_job", "N/A") == ">4" 
                                        else original_data.get('last_new_job', "N/A"),
            "Education Level": original_data.get("education_level", "N/A"),
            "Major Discipline": original_data.get("major_discipline", "N/A"),
            "City Development Index": original_data.get("city_development_index", "N/A"),
            "Company Size": "Less than 10" if original_data.get("company_size", "N/A") == "<10"
                            else "10 to 49" if original_data.get("company_size", "N/A") == "10-49"
                            else "50 to 99" if original_data.get("company_size", "N/A") == "50-99"
                            else "100 to 499" if original_data.get("company_size", "N/A") == "100-500"
                            else "500 to 999" if original_data.get("company_size", "N/A") == "500-999"
                            else "1000 to 4999" if original_data.get("company_size", "N/A") == "1000-4999"
                            else "5000 to 9999" if original_data.get("company_size", "N/A") == "5000-9999"
                            else "More than 9999" if original_data.get("company_size", "N/A") == "10000+"
                            else original_data.get("company_size", "N/A"),
            "Company Type": original_data.get("company_type", "N/A"),
            "Probability of Leaving": f"{probability:06.2%}",
            "Prediction": "Leave" if prediction == 1 else "Stay"
        }
        results_data.append(result_dict)
    df = pd.DataFrame(results_data)

    # prepare dataset for AI
    df_results = df.copy()
    df_results["Probability of Leaving"] = df_results["Probability of Leaving"].str.rstrip("%").astype(float)
    df_results["Work Experience"] = df_results["Work Experience"].apply(lambda x: 0 if x == '<1' else 21 if x == '>20' else int(x))
    df_results["Duration of Last New Job"] = df_results["Duration of Last New Job"].apply(lambda x: 0 if x == 'Never' else 5 if x == 'More than 4 years' else int(x))
    st.session_state.dataframe_results = df_results

    st.markdown('<br>', unsafe_allow_html=True)
    
    # Search by full name
    col1, col2, col3 = st.columns(3)
    with col2:
        search_name = st.text_input("Search by Full Name", key="search_name", placeholder="Search by Full Name", max_chars=200, label_visibility="collapsed")
    if search_name:
        df_search = df[df["Full Name"].str.lower() == search_name.lower()]
        if not df_search.empty:
            prob_num = float(df_search.iloc[0]["Probability of Leaving"].rstrip("%")) / 100
            st.markdown('<br>', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns([2,2,4,2], vertical_alignment="center")
            with col2:
                st.markdown(f'<p class="sub-title-3">Search Results for:</p>', unsafe_allow_html=True)
                st.markdown(f'Full Name: **{df_search.iloc[0]["Full Name"]}**')
                st.markdown(f'Prediction: **{df_search.iloc[0]["Prediction"]}**')
                st.markdown(f'Probability of Leaving: **{df_search.iloc[0]["Probability of Leaving"]}**')
            with col3:
                if df_search.iloc[0]["Prediction"] == "Leave":
                    if prob_num > 0.8:
                        st.error("Prediction: Very High Risk of Leaving")
                        with st.container(border=True):
                            st.markdown("""This employee shows an extremely high risk of changing jobs after training. Immediate intervention is recommended. 
                                        
                                        They are not suitable for participant of data science course by Asencio.""")
                    elif prob_num > 0.65:
                        st.error("Prediction: High Risk of Leaving")
                        with st.container(border=True):
                            st.markdown("""This employee shows a high risk of changing jobs after training. 
                                        
                                        They are not suitable for participant of data science course by Asencio.""")
                    else:
                        st.warning("Prediction: Moderate Risk of Leaving")
                        with st.container(border=True):
                            st.markdown("""This employee is predicted to leave, but with some uncertainty. Consider checking in regularly. 
                                        
                                        If company want to add more participant of data science course by Asencio, 
    this employee should be considered for participation.""")
                else:
                    if prob_num < 0.2:
                        st.success("Prediction: Very Likely to Stay")
                        with st.container(border=True):
                            st.markdown("""This employee shows strong indicators of remaining with the company. They appear highly satisfied with their current position. 
                                        
                                        They are top priority for participant of data science course by Asencio.""")
                    elif prob_num < 0.35:
                        st.success("Prediction: Likely to Stay")
                        with st.container(border=True):
                            st.markdown("""This employee is likely to remain with the company after training. They are second priority for participant of data science course by Asencio.

                                        They are second priority for participant of data science course by Asencio.""")
                    else:
                        st.info("Prediction: Somewhat Likely to Stay")
                        with st.container(border=True):
                            st.markdown("""This employee is predicted to stay, but with some uncertainty. Consider checking in regularly.
                                        
                                        If company want to limit participant of data science course by Asencio, 
    this employee should be considered for cancellation.""")
        else:
            st.error(f"No employees found with name containing '{search_name}'")

    st.markdown('<br>', unsafe_allow_html=True)

    # Display results dataframe
    col1, col2, col3 = st.columns([1,13,1])
    with col2:
        if len(results) < 9:
            st.dataframe(df, key="results_df_<9", hide_index=True)
        else:
            st.dataframe(df, key="results_df_>9", hide_index=True, height=350)
        st.write(f"Total predictions: {len(results)}")  
    
    st.markdown("---")

    # Ask AI
    st.markdown('<h2 class="sub-title">Ask AI</h2>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col2:
        request = st.text_area("Ask AI", key="ask_ai", height=100, placeholder="Ask AI about the results", max_chars=500, label_visibility="collapsed")
        button = st.button('Ask AI', key='ask_ai_button', use_container_width=True)
    if button and request:
        with st.spinner("AI is thinking. It may take up to 3 minutes..."):
            with st.container(border=True):
                response = ask_ai(request, st.session_state.dataframe_results.to_dict())
                if response["status"] == "error":
                    st.write(response['input'].message)
                else:
                    st.write(response["message"])
                    st.info(response["by"])     

    st.markdown("---")
    # New prediction button
    col1, col2, col3, col4 = st.columns(4)
    with col2:
        st.button("New Single Prediction", on_click=navigate_to, args=('single_input',), use_container_width=True)
    with col3:
        st.button("New Mass Prediction", on_click=navigate_to, args=('mass_input',), use_container_width=True)

    # Placeholder for future chatbot button
    


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