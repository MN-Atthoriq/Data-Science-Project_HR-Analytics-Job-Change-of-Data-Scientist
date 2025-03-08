# Job Change of Data Scientists | Data Science Project

> Data from [Kaggle](https://www.kaggle.com/datasets/arashnic/hr-analytics-job-change-of-data-scientists) with modification in the problem context.

*This project was completed as a part of Rakamin Academy Data Science Bootcamp.*

Data is the new oil, and many companies are investing in developing their employees' data science skills. However, after completing their training, many employees seek new job opportunities, leading to talent loss and wasted investment for companies. Ascencio, a leading data science consulting firm, aims to help businesses **reduce attrition rates** by **predicting which employees are likely to leave** after completing a data science course.

To achieve this, we will build **machine learning models** to predict whether an employee will seek a job change or not. For further analysis, we will also connect **AI agent** to prediction result.

## Stage 1 - Exploratory Data Analysis
### Summary
1. There is no duplicate data, either as a whole data or enrollee_id column (primary key). However, there is a lot of missing data (10203 rows or 53.26% of the dataset) and it can impact the ML model if not handled carefully.
2. The imbalance target is also the main problem in this dataset. There are only 4777 data of Leaving with 14381 data of Staying (25:75). It also happens in features like gender, major_discipline, etc with different proportions.
3. There are incorrect data in the dataset. If education_level is above 'High School', that employee shouldn't have input 'No Major' in major_discipline. They should input 'Other' if their major is not in form choices.
4. training_hours column is not relevant as a target because no feature has a correlation with training_hours. It is also not relevant as a feature since it does not correlate with the target column and it would not make sense for a company to input training_hours data while they are still determining which employees will join the course.
5. There is only one numerical feature in this dataset. It will require careful encoding for categorical features.
6. Based on EDA, for choosing participants in data science courses, Ascencio should choose employees that have relevant experience in data science, do not currently enroll in university, have lower or higher education level (primary school or PhD), have higher experience working (11 years or above), and higher years in current company (4 years or more).

### Preprocessing Data Recomendation
1. Removing the training_hours column as it is irrelevant both as a target and as a feature.
2. Perform renaming and manual imputation first according to the analysis in 1_EDA.ipynb.
3. When applying one-hot encoding, remove one additional column to avoid multicollinearity issues.
4. Use MICE to impute missing values in the dataset.
5. Apply SMOTE to handle data imbalance in the target column.
6. Note that only 10 columns will be used as features:
city_development_index, gender, relevent_experience, enrolled_university, education_level, major_discipline, experience, company_size, company_type, last_new_job.

> **Notes:**<br/>Actually, we want to build machine learning model for predicting training_hours. However, since the prediction does not involve the training_hours column, building a machine learning model for predicting training_hours will be in vain.

## Stage 2 - Preprocessing and ML
### Summary
1. After considering 35+ [combinations](https://docs.google.com/spreadsheets/d/1fHVYzMt236zO0H9nlIeZy1kKM4ujnzb5wPbysHgyq3Q/edit?gid=625641172#gid=625641172) for preprocessing dataset, we conclude that the best preprocessing dataset is:
> Drop 'city' and 'training_hours', drop rows with equal or more than 4 NaN values, ordinal encoding + ohe, MICE imputation using LinearRegression, split test_size=0.2, SMOTE with sampling_strategy=0.35, MinMaxScaler
2. We use MICE imputation using LinearRegression because it can drastically increase the accuracy of our model. Based on PR-AUC, it increased from ~40% to amazing >70%. We analyze that although this dataset is classification, this dataset is not from the real world, so using LinearRegression may break the code for creating this dataset.
3. We consider take best model based on 3 factors: first, it needs to be above 70% in PR-AUC Test. We using PR-AUC since our dataset is imbalanced (25:75). Second, it needs to have the highest Recall Test. Third, it needs to not overfitting or underfitting.
4. The best model that we will take is LGBMClassifier with Learning Curve to determine the best parameter. It resulted with 71.6% in PR-AUC Test, 76.38% in Recall Test, and 86.08% in Precision Test.
5. We can see features that impact greatly the target are: City Development Index (CDI), Company Type (Funded Startup or NGO), Gender (Female), and Experience.
6. Based on SHAP Values; higher CDI, higher Experience, higher Education Level (PhD or Master), or higher Company Size mean lower chance of leaving the company. However; currently enroll in university or do not have data science experience tends to the leave company.
7. Based on SHAP Values, higher Last New Job means higher chance to leave the company. It is different with our previous analysis when EDA. We analyze that this is because SHAP can get the hidden correlation between Last New Job to target. This hidden correlation can't be described using simple linear regression in EDA.
8. We pickle 3 objects for our FastAPI as backend in our final project. These objects are ML model, Min Max Scaler, and Label Encoding.

### Business Recomendation
1. We suggest Ascencio to search client or company with higher City Development Index (0.8-1 CDI) or have higher Company Size (5000 employees or more). It is because Ascencio can persuade clients more easily since their employee are unlikely leave the company.
2. For choosing participants in data science courses, the company should choose employee that have higher experience working (11 years or above), have higher education level (Phd or Masters), are newer in their current company (1 years or lower), do not currently enrolling in university, and/or relevant experience in data science.
3. Because we target employees that have higher experience working, Ascencio need to make curriculum of data science with focus that can easily be learned by people aged 30-40 years old.
4. Employees with STEM major or employees that have relevant experience in data science usually take this data science courses, Ascencio can make curriculum of data science that will more focus on business knowledge than math or programming.
5. If company still want to participate employee who show higher likelihood of leaving, suggest that company to implement specific retention strategies such as special contract, mentorship programs, career development plans, or special incentives.

## Stage 3 - Deployment
### Summary
1. We will use [FastAPI](https://fastapi.tiangolo.com/) for backend and [Streamlit](https://docs.streamlit.io/get-started) for frontend. We will also use [Ollama](https://ollama.com/) for AI agent by [LangChain](https://python.langchain.com/docs/introduction/) using model [Qwen2.5:7b](https://ollama.com/library/qwen2.5) and [Llama3.1:8b](https://ollama.com/library/llama3.1).
2. FastAPI can handle making excel template (for mass input), preprocessing single or mass input, predicting input using ML model, and asking to AI agent about prediction results.
3. Streamlit will show landing page, about page, single input page, mass input page, and prediction + ask AI page.
4. For deployment, Streamlit will deploy in streamlit.io and FastAPI will deploy locally using Ngrok to connect it with streamlit.

### How to Run
1. Make sure there are already Qwen2.5:7b and Llama3.1:8b installed using Ollama.
```
ollama pull qwen2.5
ollama pull llama3.1
```
2. Connect FastAPI to the internet using Ngrok (put your ngrok auth token) and copy the link.
3. Paste Ngrok link into Streamlit so they can communicate with each other.
4. Enjoy!