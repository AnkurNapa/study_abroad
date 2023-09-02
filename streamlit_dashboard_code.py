import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import seaborn as sns
from scipy.stats import chi2_contingency

# Placeholder data (replace this with your actual data)

df = pd.read_csv('Covid Student Survey Sample data.csv')

# Drop the specified columns
columns_to_drop = [
    "Response ID",
    "You mentioned you now intend to study in a different country. Please outline the country you previously planned to study in",
    "You mentioned you now intend to study in a different country. Please outline the country you now planned to study in"
]
df = df.drop(columns=columns_to_drop, errors='ignore')

# Drop rows with missing values
df.dropna(inplace=True)


# Streamlit App
st.title('Student Study Abroad and COVID-19 Impact Dashboard')


st.dataframe(df)

# ----------------------------------------------------------------------------

def generate_insights(df, question):
    top_options = df[question].value_counts().index.tolist()[:2]
    top_counts = df[question].value_counts().tolist()[:2]
    return f"- The most common responses for '{question}' are '{top_options[0]}' with {top_counts[0]} responses and '{top_options[1]}' with {top_counts[1]} responses."



# Initialize the figure for Matplotlib
plt.figure(figsize=(20, 15))

# Questions to explore
questions_to_explore = [
    "What is your preferred study destination?",
    "If vaccinated what vaccine did you receive?",
    "What is your current study status?",
    "If you changed you study abroad plans as a result of COVID-19, what was the main contributing factor that influenced your decision",
    "Have you been vaccinated?",
    "How do you feel about studying higher education online without travelling overseas?"
]
# Generate and display each plot and insight individually
for i, question in enumerate(questions_to_explore, 1):
    plt.figure(figsize=(10, 6))
    sns.countplot(y=question, data=df, order=df[question].value_counts()[:10].index)
    plt.title(f'Distribution of Responses for: "{question}"')
    plt.xlabel('Count')
    plt.ylabel('Response Options')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    st.write(f"## Graphical Insight for: {question}")
    st.pyplot(plt.gcf())
    
    insight = generate_insights(df, question)
    st.write(f"### Dynamic Insight for: {question}")
    st.write(insight)


# ----------------------------------------------------------------------------

def calculate_metric(df):
    w1, w2, w3 = 0.4, 0.3, 0.3
    vaccination_map = {'Yes - 3 doses':1, 'Yes - 2 doses': 1, '3 doses': 1, "I'm planning to be vaccinated soon": 0.5, "No (I don't intend to get vaccinated)": 0.2, 'Yes - 1 dose': 0.5}
    country_map = {'Australia': 1, 'Canada': 1, 'United States': 1, 'United Kingdom': 1, 'Still Deciding (Not Sure)': 0.5}
    educational_background_map = {'Already studying abroad': 1, 'Considering studies abroad': 1, 'Not Interested': 0.3, 'Not Sure': 0.5, 'Pursuing/ Completed High School': 0.4}

    for country in df['What is your preferred study destination?'].unique():
        if country not in country_map:
            country_map[country] = 0.5

    df['Likelihood_to_Study_Abroad_Score'] = (
        df['Have you been vaccinated?'].map(vaccination_map) * w1 +
        df['What is your preferred study destination?'].map(country_map) * w2 +
        df['What is your current study status?'].map(educational_background_map) * w3
    )

    return df

df = calculate_metric(df)

score_slider = st.slider('Likelihood to Study Abroad Score', min_value=0.0, max_value=1.0, value=(0.0, 1.0), step=0.05)
filtered_data = df[(df['Likelihood_to_Study_Abroad_Score'] >= score_slider[0]) & (df['Likelihood_to_Study_Abroad_Score'] <= score_slider[1])]

st.subheader(f'Students with Likelihood to Study Abroad Score between {score_slider[0]} and {score_slider[1]}')
st.write(filtered_data)

st.subheader('Count of Possible Students')
st.write(f'Total number of possible students to study abroad: {len(filtered_data)}')

if st.button('Mail this to Me'):
    filtered_data.to_csv('filtered_data.csv', index=False)
    st.success('Successfully mailed to me!!')


# ----------------------------------------------------------------------------



