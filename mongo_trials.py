#!/usr/bin/env python
# coding: utf-8

# In[5]:


# Get inputs from user in streamlit
# Put the inputsin the list
# Query this inputs with the database
# Fetch the filepath related to the queries
# Data Viz


# In[1]:


import pandas as pd
import json
import glob
import plotly.express as px
import streamlit as st
import pymongo
from pymongo import MongoClient

# Get the path where all the files are present (get thier names for here but in implementation direct path is sufficient)
path = "F:/A/DSML/Intern Sony/Server/*.json"
files = glob.glob(path)

# Getting file names
file_name = []
for file in files:
    split = file.split('\\')
    file_name.append(split[-1])

# Connecting to DB
cluster = MongoClient("mongodb+srv://paddipuneeth:Shipwreck9@cluster0.uyexukv.mongodb.net/?retryWrites=true&w=majority")
db = cluster["paddi"]
collection = db["tvdata"]


# Finding unique devices names is required here to test the querying
device = []
content = []
application = []

results = collection.find({})

for result in results:
    device.append(result['device'])
    content.append(result['contentid'])
    application.append(result['application'])

# Selecting 2 names for devices for testing purpose as there is no input from user 
#devicenames = device[:2]
#contentnames = content[:2]
#applicationnames = application[:2]

# Get inputs from the user in streamlit
devices = device
devices.append('All')

device_select = st.multiselect("Select the Device",devices,default = 'All')
    
if 'All' in device_select:
    device_data = device
else:
    device_data = device_select
    
application_data = []
application_user_select = []
device_query = collection.find({ "device": { "$in": device } }, { "application": 1 })
for c in device_query:
    application_data.append(c['application'])
application_user_select = application_data
application_user_select.append('All')
    
application_select = st.multiselect("Select the Application",application_user_select,default = 'All')
    
if 'All' in application_select:
    application_data = application_data
else:
    application_data = application_select
    
content_data = []
content_user_select = []
application_query = collection.find({ "application": { "$in": application_data } }, { "contentid": 1 })
for c in application_query:
    content_data.append(c['contentid'])
content_user_select = content_data
content_user_select.append('All')

content_select = st.multiselect("Select the Content",content_user_select,default = 'All')

if 'All' in content_select:
    content_data = content_data
else:
    content_data = content_select

path_name = []
content_query = collection.find({ "contentid": { "$in": content_data } }, { "path": 1 })
for c in content_query:
    path_name.append(c['path'])
st.write("The list of file names: ",path_name)
# Take this path_name put it in a for loop to read each file and concatenate to get the final dataframe for Vizn.
# END # of today
df_list = []
for file in path_name:
    name = file +'.json'
    df_one = pd.read_json(name)
    df_list.append(df_one)
df = pd.concat(df_list)
st.markdown('### Detailed Data view')
st.dataframe(df.head(5))
st.write(df.shape)





data = df

face_ids = []
for row in df['faces']:
    for face in row:
        face_ids.append(face['face_id'])
most_viewed_user = pd.DataFrame(face_ids,columns = ['users']).value_counts().sort_values(ascending=False).reset_index().iloc[0:1,:]['users'][0]

# KPI 2: Most Viewed age of the user
age_ranges = []
for i in range(len(df)):
    for face in df.iloc[i]['faces']:
        age_ranges.append(face["age"])
most_viewed_age = pd.DataFrame(age_ranges,columns = ['age']).value_counts().sort_values(ascending=False).reset_index().iloc[0:1,:]['age'][0]


age_ranges = []
faces_ids = {}
for i in range(len(data)):
    for face in data.iloc[i]['faces']:
        age_ranges.append(face["age"])
        gender = face["face_id"]
        if gender not in faces_ids:
            faces_ids[gender] = {}
        if face["age"] not in faces_ids[gender]:
            faces_ids[gender][face["age"]] = 1
        else:
            faces_ids[gender][face["age"]] += 1

df_age_gender = pd.DataFrame(faces_ids)
df_age_gender_sort = df_age_gender.transpose().reset_index().melt(id_vars = 'index')
df_age_gender_sort.sort_values(by = 'value', ascending = False, inplace = True)
df_age_gender_sort.columns = ['person_id','age','count']
fig1 = px.bar(df_age_gender_sort, x = 'age', y = 'count', color = 'person_id', barmode = 'stack')
fig1 = fig1.update_layout(xaxis_title='age')
fig1 = fig1.update_layout(yaxis_title='Count')
fig1 = fig1.update_layout(title='Users age')

face_ids = []
ages = []
genders = []
for row in data['faces']:
    for face in row:
        face_ids.append(face['face_id'])
        ages.append(face['age'])
        genders.append(face['gender'])

# Create a new DataFrame with the extracted data and reset index
df_face = pd.DataFrame({'face_id': face_ids, 'age': ages, 'gender': genders}).groupby(['face_id','gender']).size().reset_index(name='counts')
df_face['face_id'] = df_face['face_id'].astype(str)
fig2 = px.bar(df_face, x = 'face_id', y = 'counts', color = 'gender', barmode = 'stack')
fig2 = fig2.update_layout(xaxis_title='Users')
fig2 = fig2.update_layout(yaxis_title='Count')
fig2 = fig2.update_layout(title='Users gender')

# Extract the face_id and gaze columns
face_ids = []
gaze = []
for row in data['faces']:
    for face in row:
        face_ids.append(face['face_id'])
        gaze.append(face['gaze'])

# Create a new DataFrame
df_gaze = pd.DataFrame({'face_id': face_ids, 'gaze': gaze})

# Group by gaze and face_id, and get the count
df_gaze = df_gaze.groupby(['gaze','face_id']).size().reset_index(name='count')
df_gaze['face_id'] = df_gaze['face_id'].astype(str)

# Plot the bar chart
fig3 = px.bar(df_gaze, x = 'face_id', y = 'count', color = 'gaze', barmode = 'stack')
fig3 = fig3.update_layout(xaxis_title='Users')
fig3 = fig3.update_layout(yaxis_title='Gaze Count')
fig3 = fig3.update_layout(title='Gaze Count rom the users')

# function to detect maximum emotion
def emotion_detection(emotions):
    max_emotion = max(emotions, key = emotions.get)
    return max_emotion

# load json data into a DataFrame
df = data

# extract emotions column
emotions = df.apply(lambda x: [f["emotions"] for f in x["faces"]], axis = 1)
emotions = emotions.explode()

# apply emotion_detection function to emotions column
emotions["detected_emotion"] = emotions.apply(emotion_detection)
detected_emotions = emotions['detected_emotion'].value_counts().to_frame().reset_index()
detected_emotions.columns = ['emotions','count']

# create a graph of detected emotions
fig4 = px.pie(detected_emotions, values='count', names='emotions', title="Emotions Detected in the device")

emotions = []
counts = []
face_ids = []

for index, row in data.iterrows():
    for face in row['faces']:
        face_ids.append(face['face_id'])
        emotions_dict = {k:float(v) for k,v in face['emotions'].items()}
        max_emotion = max(emotions_dict, key=emotions_dict.get)
        emotions.append(max_emotion)
        counts.append(emotions_dict[max_emotion])

data_emotions_face_id = {'emotions': emotions, 'counts': counts, 'face_id': face_ids}
df_emotions_face_id = pd.DataFrame(data_emotions_face_id)

# group data by emotions, face_id and count occurrences of each face_id
df_emotions_face_id = df_emotions_face_id.groupby(['emotions', 'face_id']).count()
df_emotions_face_id = df_emotions_face_id.reset_index()
df_emotions_face_id = df_emotions_face_id.sort_values('counts',ascending = False)

fig5 = px.bar(df_emotions_face_id, x='emotions', y='counts', color='face_id', barmode='group')
fig5 = fig5.update_layout(xaxis_title='Emotions')
fig5 = fig5.update_layout(yaxis_title='Count')
fig5 = fig5.update_layout(title='Emotions of each user')

emotions = []
counts = []
gender = []

for index, row in data.iterrows():
    for face in row['faces']:
        gender.append(face['gender'])
        emotions_dict = {k:float(v) for k,v in face['emotions'].items()}
        max_emotion = max(emotions_dict, key=emotions_dict.get)
        emotions.append(max_emotion)
        counts.append(emotions_dict[max_emotion])

data_emotions_gender = {'emotions': emotions, 'counts': counts, 'gender': gender}
df_emotions_gender = pd.DataFrame(data_emotions_gender)

# group data by emotions, gender and count occurrences of each gender
df_emotions_gender = df_emotions_gender.groupby(['emotions', 'gender']).count()
df_emotions_gender = df_emotions_gender.reset_index()
df_emotions_gender = df_emotions_gender.sort_values('counts',ascending = False)

fig6 = px.bar(df_emotions_gender, x='emotions', y='counts', color='gender', barmode='group')
fig6 = fig6.update_layout(xaxis_title='Emotions')
fig6 = fig6.update_layout(yaxis_title='Count')
fig6 = fig6.update_layout(title='Emotions wrt gender')

emotions = []
counts = []
age = []

for index, row in data.iterrows():
    for face in row['faces']:
        age.append(face['age'])
        emotions_dict = {k:float(v) for k,v in face['emotions'].items()}
        max_emotion = max(emotions_dict, key=emotions_dict.get)
        emotions.append(max_emotion)
        counts.append(emotions_dict[max_emotion])

data_emotions_age = {'emotions': emotions, 'counts': counts, 'age': age}
df_emotions_age = pd.DataFrame(data_emotions_age)

# group data by emotions, age and count occurrences of each age
df_emotions_age = df_emotions_age.groupby(['emotions', 'age']).count()
df_emotions_age = df_emotions_age.reset_index()
df_emotions_age = df_emotions_age.sort_values('counts',ascending = False)

fig7 = px.bar(df_emotions_age, x='emotions', y='counts', color='age', barmode='group')
fig7 = fig7.update_layout(xaxis_title='Emotions')
fig7 = fig7.update_layout(yaxis_title='Count')
fig7 = fig7.update_layout(title='Emotions wrt age')

placeholder = st.empty()

with placeholder.container():
    # create three columns
    kpi1, kpi2 = st.columns(2)

    # fill in those three columns with respective metrics or KPIs 
    kpi1.metric(label="most_viewed_user", value=most_viewed_user)
    kpi2.metric(label="most_viewed_user's age ⏳", value= most_viewed_age)
    # create two columns for charts 

    fig_col1, fig_col2 = st.columns(2)

    with fig_col1:
        #st.markdown("### DEVICE 1")
        #st.markdown("### Emotions Distribution")
        #st.markdown("Problems related to users", unsafe_allow_html=True, style={"text-align": "center"})
        st.markdown("### Problems related to users")
        st.markdown("Multiple age Assigned to the user")
        st.write(fig1)       
        #fig3 = px.histogram(data_frame = df, x = 'person_count')

    with fig_col2:
        st.markdown("Multiple age Assigned to the user")
        st.write(fig2)


    with fig_col1:
        st.markdown("Gaze is too much biased towards looking at")
        st.write(fig3)       
        #fig3 = px.histogram(data_frame = df, x = 'person_count')

    with fig_col2:
        st.markdown("### Emotion Analysis")
        st.write(fig4)


    with fig_col1:
        #st.markdown("Emotion Analysis", unsafe_allow_html=True, style={"text-align": "center"})
        st.write(fig5)       
        #fig3 = px.histogram(data_frame = df, x = 'person_count')


    with fig_col2:
        st.write(fig6)

    with fig_col1:
     
        st.write(fig7)       
        #fig3 = px.histogram(data_frame = df, x = 'person_count')
# In[ ]:




