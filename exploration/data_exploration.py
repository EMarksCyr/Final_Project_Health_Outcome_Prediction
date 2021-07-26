# import dependencies
import psycopg2
import pandas as pd
import numpy as np

from getpass import getpass

password = getpass("Enter database password")

param_dic = {
    "host": "localhost",
    "database": "BRFSSAnalysis",
    "user": "postgres",
    "password": password,
}


def connect(params_dic):
    """
    Tranform a SELECT query into a pandas dataframe
    """
    conn = None
    try:
        # connect to the PostgreSQL server
        print("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(**params_dic)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1)
    print("Connection successful")
    return conn


def postgresql_to_dataframe(conn, select_query, column_names):
    """
    SELECT * from question_info
    """
    cursor = conn.cursor()
    try:
        cursor.execute(select_query)
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        cursor.close()
        return 1

    # Naturally we get a list of tupples
    tupples = cursor.fetchall()
    cursor.close()

    # We just need to turn it into a pandas dataframe
    df = pd.DataFrame(tupples, columns=column_names)
    return df


# Connect to the database
conn = connect(param_dic)
column_names = ["id", "var_name", "label", "text"]
# Execute the "SELECT *" query to save question_info as a datafram
question_info_df = postgresql_to_dataframe(
    conn, "select * from question_info", column_names
)

# Connect to the database and repeat process for question_values
conn = connect(param_dic)
column_names = ["id", "question_id", "label", "value", "value_end"]
# Execute the "SELECT *" query to save question_info as a datafram
answer_info_df = postgresql_to_dataframe(
    conn, "select * from question_values", column_names
)


# determing which columns of user answers (aka relevant answers) to bring over
a = question_info_df["label"].values.tolist()
b = question_info_df["var_name"].values.tolist()


zip_iterator = zip(b, a)
a_dictionary = dict(zip_iterator)


# select columns to include from list above for health behaviour features predicting general, mental and physical health
columns = [
    "id",
    "_STATE",
    "GENHLTH",
    "PHYSHLTH",
    "MENTHLTH",
    "POORHLTH",
    "EXRACT11",
    "PAFREQ1_",
    "_MINAC11",
    "ACTIN12_",
    "EXRACT21",
    "PAFREQ2_",
    "_MINAC21",
    "ACTIN22_",
    "STRFREQ_",
    "PA2MIN_",
    "_METSTAT",
    "_URBSTAT",
    "HTIN4",
    "WTKG3",
    "_BMI5",
    "_SMOKER3",
    "_DRNKWK1",
    "FC601_",
    "FTJUDA2_",
    "GRENDA1_",
    "VEGEDA2_",
    "POTADA1_",
    "FRNCHDA_",
    "_FRUTSU1",
    "_VEGESU1",
    "_PAINDX2",
    "_PASTRNG",
    "_AGE80",
]

# Connect to the database and repeat process for user_answers: limit of 500
conn = connect(param_dic)
column_names = columns
# Execute the "SELECT *" query to save question_info as a datafram
health_behaviour_df = postgresql_to_dataframe(
    conn,
    f"select id, _STATE, GENHLTH, PHYSHLTH, MENTHLTH, POORHLTH, EXRACT11, PAFREQ1_, _MINAC11, ACTIN12_, EXRACT21, PAFREQ2_, _MINAC21, ACTIN22_,  STRFREQ_, PA2MIN_, _METSTAT, _URBSTAT, HTIN4, WTKG3, _BMI5, _SMOKER3, _DRNKWK1, FC601_, FTJUDA2_,  GRENDA1_, VEGEDA2_, POTADA1_, FRNCHDA_, _FRUTSU1, _VEGESU1,  _PAINDX2, _PASTRNG, _AGE80 from user_answers",
    column_names,
)


# filling blank spaces with NaN
health_behaviour_df = health_behaviour_df.fillna(value=np.nan)

# Make a copy of health_behaviour_df to perform value recoding on
recoded_health_behaviour_df = health_behaviour_df.copy()

# ## TODO: go through features and correct poorly coded values (e.g. 9999 = no answer)
# clean up DF for null values
# clean up poorly encoded variables

# ### GENHLTH
# #### question: Would you say that in general your health is:
#
# Answers currently coded as :
#    - 1: Excellent
#    - 2: Very Good
#    - 3: Good
#    - 4: Fair
#    - 5: Poor
#    - 7: Don't know/Not Sure
#    - 9: Refused
#    - BLANK: Not asked or Missing
#
# Recode to:
#    - Nan: Don't know/Not Sure
#    - Nan: Refused
#    - BLANK: Not asked or Missing
#    - 1: Poor
#    - 2: Fair
#    - 3: Good
#    - 4: Very Good
#    - 5: Excellent
#


# convert column to int
recoded_health_behaviour_df.GENHLTH = pd.to_numeric(
    recoded_health_behaviour_df.GENHLTH
).astype(int)
recoded_health_behaviour_df["GENHLTH"].dtypes


# recode GENHLTH values to new coding scheme described above
recoded_health_behaviour_df.loc[health_behaviour_df.GENHLTH == 1.0, "GENHLTH"] = 5
recoded_health_behaviour_df.loc[health_behaviour_df.GENHLTH == 2.0, "GENHLTH"] = 4
recoded_health_behaviour_df.loc[health_behaviour_df.GENHLTH == 3.0, "GENHLTH"] = 3
recoded_health_behaviour_df.loc[health_behaviour_df.GENHLTH == 4.0, "GENHLTH"] = 2
recoded_health_behaviour_df.loc[health_behaviour_df.GENHLTH == 5.0, "GENHLTH"] = 1
recoded_health_behaviour_df.loc[health_behaviour_df.GENHLTH == 7.0, "GENHLTH"] = np.NaN
recoded_health_behaviour_df.loc[health_behaviour_df.GENHLTH == 9.0, "GENHLTH"] = np.NaN


recoded_health_behaviour_df.GENHLTH = pd.to_numeric(
    recoded_health_behaviour_df.GENHLTH
).astype("Int32")


print(recoded_health_behaviour_df.isnull().sum())


# ### PA2MIN_
# #### Question:  Minutes of total Physical Activity per week
# Originally coded as:
# - 0-99999: Minutes of Activity per week
# - BLANK: not asked or missing
#

recoded_health_behaviour_df.PA2MIN_ = pd.to_numeric(
    recoded_health_behaviour_df.PA2MIN_
).astype("Int32")
recoded_health_behaviour_df["PA2MIN_"].dtypes


# ### PHYSHLTH
# #### Question:  Now thinking about your physical health, which includes physical illness and injury, for how many days during the past 30 days was your physical health not good?
# Answers originally coded as:
# - 1-30: Number of Days, numeric
# - 88: None
# - 77: Don't know/Not sure
# - 99: Refused
# - Blank: Not asked or missing
#
# Recode to:
#
# - 1-30: Number of Days, int
# - 0: None
# - Nan: Don't know/Not sure
# - Nan: Refused
# - Blank: Not asked or missing
#

# recode PHYSHLTH values to new coding scheme described above
recoded_health_behaviour_df.loc[health_behaviour_df.PHYSHLTH == 88, "PHYSHLTH"] = 0
recoded_health_behaviour_df.loc[health_behaviour_df.PHYSHLTH == 77, "PHYSHLTH"] = np.NaN
recoded_health_behaviour_df.loc[health_behaviour_df.PHYSHLTH == 99, "PHYSHLTH"] = np.NaN

# convert column from object to int
recoded_health_behaviour_df.PHYSHLTH = pd.to_numeric(
    recoded_health_behaviour_df.PHYSHLTH
).astype("Int32")


# ### MENTHLTH
# #### Question:  Now thinking about your mental health, which includes stress, depression, and problems with emotions, for how many days during the past 30 days was your mental health not good?
# Answers originally coded as:
# - 1-30: Number of Days, numeric
# - 88: None
# - 77: Don't know/Not sure
# - 99: Refused
# - Blank: Not asked or missing
#
# Recode to:
#
# - 1-30: Number of Days, int
# - 0: None
# - Nan: Don't know/Not sure
# - Nan: Refused
# - Blank: Not asked or missing
#


# recode PHYSHLTH values to new coding scheme described above
recoded_health_behaviour_df.loc[health_behaviour_df.MENTHLTH == 88, "MENTHLTH"] = 0
recoded_health_behaviour_df.loc[health_behaviour_df.MENTHLTH == 77, "MENTHLTH"] = np.NaN
recoded_health_behaviour_df.loc[health_behaviour_df.MENTHLTH == 99, "MENTHLTH"] = np.NaN

# convert column from object to int
recoded_health_behaviour_df.MENTHLTH = pd.to_numeric(
    recoded_health_behaviour_df.MENTHLTH
).astype("Int32")

# ### _PAINDX2
# #### Question:  Physical Activity Index
# Values originally coded as:
# - 1: Meet Aerobic Recommendations
# - 2: Did Not Meet Aerobic Recommendations
# - 9: Don’t know/Not Sure/Refused/Missing
#
# Recode to:
# - 1: Meet Aerobic Recommendations
# - 2: Did Not Meet Aerobic Recommendations
# - Nan: Don’t know/Not Sure/Refused/Missing
#

# recode values to new coding scheme described above
recoded_health_behaviour_df.loc[health_behaviour_df._PAINDX2 == 9, "_PAINDX2"] = np.NaN
recoded_health_behaviour_df._PAINDX2 = pd.to_numeric(
    recoded_health_behaviour_df._PAINDX2
).astype("Int32")

# ### _PASTRNG
# #### Question:  Muscle Strengthening Recommendation
# Originally coded as:
# - 1: Meet muscle strengthening recommendations
# - 2: Did not meet muscle strengthening recommendations
# - 9: Don’t know/Not Sure/Refused/Missing
#
# Recode to:
# - 1: Meet muscle strengthening recommendations
# - 2: Did not meet muscle strengthening recommendations
# - Nan: Don’t know/Not Sure/Refused/Missing

# recode values to new coding scheme described above
recoded_health_behaviour_df.loc[health_behaviour_df._PASTRNG == 9, "_PASTRNG"] = np.NaN
recoded_health_behaviour_df._PASTRNG = pd.to_numeric(
    recoded_health_behaviour_df._PASTRNG
).astype("Int32")

# ### _FRUTSU1
# #### Question:  Total fruits consumed per day
# Originally coded as:
# - 0-99998: Number of Fruits consumed per day (two implied decimal places)
# - BLANK: Not asked or Missing
#
# Recode to:
# - 0.00-999.98: Number of Fruits consumed per day
# - Nan: Not asked or Missing

# TODO: convert to int to remove decimal place, convert to string then interate through and insert decimal before last two digits, convert to float


# In[93]:


recoded_health_behaviour_df["_FRUTSU1"] = (
    recoded_health_behaviour_df["_FRUTSU1"].fillna(100000).astype(float)
)

recoded_health_behaviour_df["_FRUTSU1"] = (
    recoded_health_behaviour_df["_FRUTSU1"].div(100).round(2)
)


recoded_health_behaviour_df["_FRUTSU1"] = recoded_health_behaviour_df["_FRUTSU1"].mask(
    np.isclose(recoded_health_behaviour_df["_FRUTSU1"].values, 1000.00)
)


# ###  _VEGESU1
# #### Question:  Total vegetables consumed per day
# Originally coded as:
# - 0-99998: Number of Vegetables consumed per day (two implied decimal places)
# - BLANK: Not asked or Missing
#
# Recode to:
# - 0.00-999.98: Number of Vegetables consumed per day
# - Nan: Not asked or Missing

recoded_health_behaviour_df["_VEGESU1"] = (
    recoded_health_behaviour_df["_VEGESU1"].fillna(100000).astype(float)
)
recoded_health_behaviour_df["_VEGESU1"] = (
    recoded_health_behaviour_df["_VEGESU1"].div(100).round(2)
)
recoded_health_behaviour_df["_VEGESU1"] = recoded_health_behaviour_df["_VEGESU1"].mask(
    np.isclose(recoded_health_behaviour_df["_VEGESU1"].values, 1000.00)
)


recoded_health_behaviour_df.groupby("_STATE")["_VEGESU1"].mean()


# ### State Codes
# original code:
# - 1: Alabama
# - 2	Alaska
# - 4	Arizona
# - 5	Arkansas
# - 6	California
# - 8	Colorado
# - 9	Connecticut
# - 10	Delaware
# - 11	District of Columbia
# - 12	Florida
# - 13	Georgia
# - 15	Hawaii
# - 16	Idaho
# - 17	Illinois
# - 18	Indiana
# - 19	Iowa
# - 20	Kansas
# - 21	Kentucky
# - 22	Louisiana
# - 23	Maine
# - 24	Maryland
# - 25	Massachusetts
# - 26	Michigan
# - 27	Minnesota
# - 28	Mississippi
# - 29	Missouri
# - 30	Montana
# - 31	Nebraska
# - 32	Nevada
# - 33	New Hampshire
# - 35	New Mexico
# - 36	New York
# - 37	North Carolina
# - 38	North Dakota
# - 39	Ohio
# - 40	Oklahoma
# - 41	Oregon
# - 42	Pennsylvania
# - 44	Rhode Island
# - 45	South Carolina
# - 46	South Dakota
# - 47	Tennessee
# - 48	Texas
# - 49	Utah
# - 50	Vermont
# - 51	Virginia
# - 53	Washington
# - 54	West Virginia
# - 55	Wisconsin
# - 56	Wyoming
# - 66	Guam
# - 72	Puerto Rico
#

##TODO: test on larger dataset


# ### Health Behaviours Chloropleth maps by state


import plotly.express as px

# https://plotly.com/python/choropleth-maps/


fig = px.choropleth(
    locations=["KY"], locationmode="USA-states", color=[1.80927], scope="usa"
)
fig.show()


# In[105]:


## percieved health across age
df = recoded_health_behaviour_df[["_AGE80", "PA2MIN_"]].copy()
df.head()


# In[116]:


df = df.dropna(axis=0, how="any")


# In[118]:


##TODO: remove outliers of PA2MIN_


# In[117]:


fig = px.scatter(df, x="_AGE80", y="PA2MIN_")
fig.show()


# In[ ]:


# TODO: make a dataframe that contains the demographic information of the sample and their health outcomes
# Draw up summary of sample


# In[ ]:


# In[ ]:


# map health outcomes accross states


# In[ ]:


# create a large df with demographic and health behaviour info and create model that can predict health outcomes


# In[ ]:
