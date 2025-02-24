from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from pyngrok import ngrok
import uvicorn
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Dict, Any
import pandas as pd
import joblib
from sklearn.preprocessing import OrdinalEncoder, MinMaxScaler
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl import Workbook, utils
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.comments import Comment
from io import BytesIO
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()
ngrok_auth_token = os.getenv('NGROK_AUTH_TOKEN')
if not ngrok_auth_token:
  raise Exception("NGROK_AUTH_TOKEN not found in environment variables")

  
# Expose the FastAPI app with ngrok
ngrok.set_auth_token(ngrok_auth_token)

# Create FastAPI app
app = FastAPI(
    title="Employee Prediction API",
    description="API for predicting employee job change after course completion",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Load pickle
try:
    ordinalencoder = joblib.load('fastapi\pickle\ordinalencoder.pkl')
    minmaxscaler = joblib.load('fastapi\pickle\minmaxscaler.pkl')
    model = joblib.load('fastapi\pickle\lclgbm.pkl')
except Exception as e:
  raise Exception("Error loading pickle")

# Class
## Class: categorical columns
class gender_cat(str, Enum):
  male = 'Male'
  female = 'Female'
  other = 'Other'

class enrolled_university_cat(str, Enum):
  no_enroll = 'No Enroll'
  part_time = 'Part Time'
  full_time = 'Full Time'

class education_level_cat(str, Enum):
  primary_school = 'Primary School'
  high_school = 'High School'
  graduate = 'Graduate'
  masters = 'Masters'
  phd = 'Phd'

class major_discipline_cat(str, Enum):
  stem = 'STEM'
  humanities = 'Humanities'
  business_degree = 'Business Degree'
  arts = 'Arts'
  no_major = 'No Major'
  other = 'Other'

class experience_cat(str, Enum):
  zero_exp = '<1'
  one_exp = '1'
  two_exp = '2'
  three_exp = '3'
  four_exp = '4'
  five_exp = '5'
  six_exp = '6'
  seven_exp = '7'
  eight_exp = '8'
  nine_exp = '9'
  ten_exp = '10'
  eleven_exp = '11'
  twelve_exp = '12'
  thirteen_exp = '13'
  fourteen_exp = '14'
  fifteen_exp = '15'
  sixteen_exp = '16'
  seventeen_exp = '17'
  eighteen_exp = '18'
  nineteen_exp = '19'
  twenty_exp = '20'
  more_exp = '>20'

class company_size_cat(str, Enum):
  less_10 = '<10'
  around_10_49 = '10-49'
  around_50_99 = '50-99'
  around_100_499 = '100-500'
  around_500_999 = '500-999'
  around_1000_4999 = '1000-4999'
  around_5000_9999 = '5000-9999'
  more_10000 = '10000+'

class company_type_cat(str, Enum):
  pvt_ltd = 'Pvt Ltd'
  public_sector = 'Public Sector'
  funded_startup = 'Funded Startup'
  early_startup = 'Early Startup'
  ngo = 'NGO'
  other = 'Other'

class last_new_job_cat(str, Enum):
  never = 'never'
  one = '1'
  two = '2'
  three = '3'
  four = '4'
  more_four = '>4'

## Class: Combine into one input
class EmployeeData(BaseModel):
  full_name: str = Field(..., max_length = 200)
  city_development_index: float = Field(..., ge = 0, le = 1)
  gender: gender_cat
  relevant_experience: bool = Field(...)
  enrolled_university: enrolled_university_cat
  education_level: education_level_cat
  major_discipline: major_discipline_cat
  experience: experience_cat
  company_size: company_size_cat
  company_type: company_type_cat
  last_new_job: last_new_job_cat

  class Config:
    schema_extra = {
      "example": {
        "full_name": "John Doe",
        "city_development_index": 0.5,
        "gender": "Male",
        "relevant_experience": True,
        "enrolled_university": "No Enroll",
        "education_level": "Graduate",
        "major_discipline": "STEM",
        "experience": "1",
        "company_size": "10-49",
        "company_type": "Public Sector",
        "last_new_job": "1"
      }
    }

## Class: Mass input
class MassInputData(BaseModel):
  employees: List[EmployeeData]

## Class: Preprocessed Data
class PreprocessedData(BaseModel):
  original_data: List[Dict[str,Any]]
  preprocessed_features: List[Dict[str,float]]
  features_columns: List[str]

# Map and Column
## gender
gender_map = {
    "Female": [1, 0],
    "Male": [0, 1],
    "Other": [0, 0]
    }
gender_columns = [
    "gender_Female",
    "gender_Male"
    ]
## major_discipline
major_discipline_map = {
    "Arts": [1, 0, 0, 0, 0],
    "Business Degree": [0, 1, 0, 0, 0],
    "Humanities": [0, 0, 1, 0, 0],
    "No Major": [0, 0, 0, 1, 0],
    "STEM": [0, 0, 0, 0, 1],
    "Other": [0, 0, 0, 0, 0]
  }
major_discipline_columns = [
    "major_discipline_Arts",
    "major_discipline_Business Degree",
    "major_discipline_Humanities",
    "major_discipline_No Major",
    "major_discipline_STEM"
  ]
## company_type
company_type_map = {
    "Early Startup": [1, 0, 0, 0, 0],
    "Funded Startup": [0, 1, 0, 0, 0],
    "NGO": [0, 0, 1, 0, 0],
    "Public Sector": [0, 0, 0, 1, 0],
    "Pvt Ltd": [0, 0, 0, 0, 1],
    "Other": [0, 0, 0, 0, 0]
  }
company_type_columns = [
    "company_type_Early Startup",
    "company_type_Funded Startup",
    "company_type_NGO",
    "company_type_Public Sector",
    "company_type_Pvt Ltd"
  ]


# Func: Create Excel Template
## Sub-Func: Create Header
def header_name(ws,header_list,comment_list,width_list):
  for col_num, (headers,comments,widths) in enumerate(zip(header_list,comment_list,width_list),1):
    # initiate cell
    cell = ws.cell(row=1,column=col_num)
    # fill headers with text
    cell.value = headers
    # fill headers with comment
    cell.comment = Comment(comments, 'author', width=250, height=100)
    # style headers
    cell.font = Font(bold=True)
    cell.alignment = Alignment(horizontal='center')
    cell.fill = PatternFill(start_color='00FFFF00',end_color='00FFFF00',fill_type='solid')
    # resize headers
    column_letter = utils.get_column_letter(col_num)
    ws.column_dimensions[column_letter].width = widths

## Sub-Func: Create Data Validation
def data_validation(ws,type,formula1,area):
  if type == 'list':
    dv = DataValidation(type=type, formula1=formula1, allow_blank=True)
    # pop up for instruction
    dv.promptTitle = 'List Selection'
    dv.prompt = 'Please select from the list'
    # if input not in data validation criteria
    dv.errorTitle = 'Invalid Entry'
    dv.error ='Your entry is not in the list'

  elif type == 'decimal':
    dv = DataValidation(type=type, operator='between',formula1=formula1, formula2=1, allow_blank=True)
    # pop up for instruction
    dv.promptTitle = 'Decimal Input'
    dv.prompt = 'Please input decimal number in range between 0 to 1'
    # if input not in data validation criteria
    dv.errorTitle = 'Invalid Entry'
    dv.error ='Your entry must decimal number in range between 0 to 1'

  elif type == 'whole':
    dv = DataValidation(type=type, operator='between',formula1=formula1, formula2=21, allow_blank=True)
    # pop up for instruction
    dv.promptTitle = 'Whole Number Input'
    dv.prompt = 'Please input whole number in range between 0 to 21'
    # if input not in data validation criteria
    dv.errorTitle = 'Invalid Entry'
    dv.error ='Your entry must be whole number in range between 0 to 21'

  else:
    print('Invalid type')

  # show error and input message
  dv.showErrorMessage = True
  dv.showInputMessage = True
  # add data validation
  ws.add_data_validation(dv)
  dv.add(area)

## Main-Func: Excel
def generate_excel_template():
  # initiate excel
  wb = Workbook()
  ws = wb.active
  ws.title = 'Mass Input'
  # initiate header, comment, and width list
  header_list = ['Full Name','Gender','Enrolled University','Work Experience','Data Science Experience','Duration of Last New Job','Education Level','Major Discipline',
                'City Development Index','Company Size','Company Type']
  comment_list = [
      'Enter the full name of the employee.',
      'Select the gender of the employee.',
      'Specify whether the employee is curently enroll in a university.',
      'Enter the total years of employee’s work experience. If more than 20 years, input ’21’.',
      'Specify if employee have relevant experience in data science.',
      'Enter the duration (in years) since the employee’s last new job.',
      'Specify the highest education level achieved by the employee.',
      'Specify the major discipline of the employee’s highest qualification. If the employee’s highest education level is High School or lower, input ’No Major’.',
      'Input the City Development Index (a metric representing the level of urban development) for the location where the company is based.',
      'Specify the size of the company based on the number of employees.',
      'Enter the type of company.'
  ]
  width_list = [25] * 11
  # initiate headers
  header_name(ws,header_list,comment_list,width_list)
  # add data validation to each columns
  # a. fullname
  # no data validation
  # b. gender
  data_validation(ws,"list",'"Male,Female,Other"','B2:B1001')
  # c. enrolled_university
  data_validation(ws,"list",'"No Enroll,Part Time,Full Time"','C2:C1001')
  # d. experience
  data_validation(ws,"whole",0,'D2:D1001')
  # e. relevant_experience
  data_validation(ws,"list",'"Yes,No"','E2:E1001')
  # f. last_new_job
  data_validation(ws,"list",'"Never,1,2,3,4,More than 4"','F2:F1001')
  # g. education_level
  data_validation(ws,"list",'"Primary School,High School,Graduate,Masters,Phd"','G2:G1001')
  # h. major_discipline
  data_validation(ws,"list",'"STEM,Humanities,Business Degree,Arts,No Major,Other"','H2:H1001')
  # i. city_development_index
  data_validation(ws,"decimal",0,'I2:I1001')
  # j. company_size
  data_validation(ws,"list",'"Less than 10,10 to 49,50 to 99,100 to 499,500 to 999,1000 to 4999,5000 to 9999,More than 9999"','J2:J1001')
  # k. company_type
  data_validation(ws,"list",'"Pvt Ltd,Public Sector,Funded Startup,Early Startup,NGO,Other"','K2:K1001')
  # Save the workbook to an in-memory file
  file_stream = BytesIO()
  wb.save(file_stream)
  file_stream.seek(0)
  return file_stream

@app.get("/")
async def read_root():
    """Check if API is running and pickle files are loaded"""
    return {
      "status": "API running",
      "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      "pickle_files": all([ordinalencoder, minmaxscaler, model])
      }

@app.get("/create_excel_template")
async def create_excel_template():
    """Generate and return an Excel template for mass input"""
    try:
        excel_file = generate_excel_template()
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=mass_input_template.xlsx"}
        )
    except Exception as e:
      raise HTTPException(
        status_code=500, 
        detail="Failed to generate Excel template"
      )

@app.post("/preprocess", response_model=PreprocessedData)
async def preprocess_data(data: MassInputData):
  """Preprocess employee(s) data for prediction (encoding and scaling)"""
  try:
    # Convert to dataframe
    df = pd.DataFrame([item.dict() for item in data.employees])
    # Store original data
    original_data = df.to_dict('records')
    # Divide columns
    oe_columns = ['relevant_experience', 'enrolled_university', 'education_level', 'experience', 'company_size', 'last_new_job']
    ohe_columns = ['gender','major_discipline','company_type']
    numerical_columns = ['city_development_index']
    # Ordinal Encoder oe_columns
    df[oe_columns] = ordinalencoder.transform(df[oe_columns])
    # One Hot Encoding ohe_columns
    gender_values = df['gender'].map(gender_map).tolist()
    major_discipline_values = df['major_discipline'].map(major_discipline_map).tolist()
    company_type_values = df['company_type'].map(company_type_map).tolist()
    gender_df = pd.DataFrame(gender_values, columns=gender_columns)
    major_discipline_df = pd.DataFrame(major_discipline_values, columns=major_discipline_columns)
    company_type_df = pd.DataFrame(company_type_values, columns=company_type_columns)
    df = pd.concat([df, gender_df, major_discipline_df, company_type_df], axis=1)
    # Drop unwanted columns
    df = df.drop(columns=ohe_columns)
    df = df.drop(columns='full_name')
    # Min Max Scaler
    df_values = minmaxscaler.transform(df)
    df = pd.DataFrame(df_values, columns=df.columns)
    # Store preprocessed features
    preprocessed_features = df.to_dict('records')
    # Store features columns
    features_columns = df.columns.tolist()
    return PreprocessedData(
        original_data=original_data,
        preprocessed_features=preprocessed_features,
        features_columns=features_columns
        )
  except Exception as e:
    raise HTTPException(
        status_code=500,
        detail=f"Error in preprocessing: {str(e)}"
    )

@app.post("/predict")
async def predict_data(data: PreprocessedData):
  """Make predictions based on preprocessed data"""
  try:
    # Convert PreprocessedData to dataframe
    df_final = pd.DataFrame(
              data.preprocessed_features,
              columns=data.features_columns
          )
    # Make predictions using model
    predictions = model.predict(df_final)
    probabilities = model.predict_proba(df_final)[:, 1]
    # Combine predictions with original data
    results = []
    for orig, pred, prob in zip(data.original_data, predictions, probabilities):
      results.append(
          {
              "original_data": orig,
              "prediction": pred,
              "probability": prob
          }
      )
    return {
        'status': 'success',
        'results': results
    }
  except Exception as e:
    raise HTTPException(
        status_code=500,
        detail=f"Error in prediction: {str(e)}"
    )


if __name__ == "__main__":
    # Connect to ngrok
    url = ngrok.connect(8000)
    print(f"Public URL: {url}")

    # Run the app with Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)