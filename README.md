# Job Change of Data Scientists | Data Science Project

> Data from [Kaggle](https://www.kaggle.com/datasets/arashnic/hr-analytics-job-change-of-data-scientists) with modification in problem context.

*This project was completed as a part of Rakamin Academy Data Science Bootcamp.*

Ascencio, a leading Data Science agency, offers training courses to companies to enhance their employees' skills. Companies want to predict which employees are **unlikely to seek a job change** after completing the course, as well as identify those who are **likely to finish it quickly**. By focusing on employees who are committed to staying and can contribute sooner, Ascencio helps companies optimize their training investments.

To achieve this, Ascencio will build two machine learning models: one to predict the training hours needed for an employee to complete the course, and another to predict whether an employee will seek a job change or not.

## Stage 1 - EDA and Business Insight 
### Preprocessing Data Reccomendation
1. Removing the training_hours column as it is irrelevant both as a target and as a feature. It is not relevant as a target because no feature has a correlation with training_hours. It is also not relevant as a feature since it does not correlate with the target column and it would not make sense for a company to input training_hours data while they are still determining which employees will join the course.
2. Perform renaming, grouping, and manual imputation first according to the analysis in 1_EDA_Stage-1.ipynb.
3. When applying one-hot encoding, remove one additional column to avoid multicollinearity issues.
4. Use an ML model (LGBM Classifier) to impute missing values in the dataset.
5. Apply SMOTE to handle data imbalance in the target column.
6. Note that only 10 categorical columns will be used as features:
city_development_index, gender, relevent_experience, enrolled_university, education_level, major_discipline, experience, company_size, company_type, last_new_job.

**Notes:**<br/>Since the prediction does not involve the training_hours column, we will only build ML model for predict target column

### Business Reccomendation
1. Since employee who tend to leave from company after data science courses are work in lower city development index, we suggest to Ascencio for searching client or company from higher city development index (0.8-1 CDI). It is becauses Ascencio can persuade client more easily since their employee unlikely leave the company.
2. For choosing participant of data science courses, Ascencio should choose employee that have relevant experience in data science, not enroll in university as part time or full time, have lower or higher education level (primary school or phd), higher experience working (11 years or above), and higher years in current company (4 years or more).
3. Because we target employee that have higher experience working and higher years in current company, Ascencio need to make curriculum of data science with focus that can easily learn by people with age of 30-50 years old.
4. Employee with STEM major or employee that have relevant experience in data science usually take this data science courses, Ascencio can make curriculum of data science that will more focus in business knowledge than math or programming.
