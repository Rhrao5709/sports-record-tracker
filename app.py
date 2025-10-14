import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# Load the datasets
# Assuming the CSV files are in the same directory as the app
df_men = pd.read_csv("Men_Track_Record_Comparison.csv")
df_women = pd.read_csv("Women_Track_Record_Comparison.csv")

# Combine the datasets
df = pd.concat([df_men, df_women], ignore_index=True)

# Convert 'Yes'/'No' to boolean for easier computation (True for Yes, False for No)
bool_columns = [
    'Predicted_World_Record_Breaker', 'World_Record_Correct',
    'Actual_World_Record_Breaker', 'Actual_National_Record_Breaker',
    'Actual_Personal_Best_Breaker'
]
for col in bool_columns:
    df[col] = df[col].map({'Yes': True, 'No': False, 'Unknown': None})  # Handle 'Unknown' as None

# Streamlit App Title
st.title("Track Record Comparison Dashboard")

# Sidebar for Filters
st.sidebar.header("Filters")

# Filter by Competitor Name
search_name = st.sidebar.text_input("Search by Competitor Name", "")

# Filter by Sex
sex_options = df['Sex'].unique().tolist()
selected_sex = st.sidebar.multiselect("Select Sex", options=sex_options, default=sex_options)

# Filter by Discipline
discipline_options = sorted(df['Discipline'].unique().tolist())
selected_discipline = st.sidebar.multiselect("Select Discipline", options=discipline_options, default=discipline_options)

# Filter by Nationality
nationality_options = sorted(df['Nationality'].unique().tolist())
selected_nationality = st.sidebar.multiselect("Select Nationality", options=nationality_options, default=[])

# Filter by Predicted World Record Breaker
predicted_breaker_options = ['Yes', 'No']
selected_predicted_breaker = st.sidebar.multiselect("Predicted World Record Breaker", options=predicted_breaker_options, default=predicted_breaker_options)
selected_predicted_breaker = [True if x == 'Yes' else False for x in selected_predicted_breaker]

# Filter by Actual World Record Breaker
actual_breaker_options = ['Yes', 'No']
selected_actual_breaker = st.sidebar.multiselect("Actual World Record Breaker", options=actual_breaker_options, default=actual_breaker_options)
selected_actual_breaker = [True if x == 'Yes' else False for x in selected_actual_breaker]

# Apply Filters
filtered_df = df[
    (df['Sex'].isin(selected_sex)) &
    (df['Discipline'].isin(selected_discipline)) &
    (df['Predicted_World_Record_Breaker'].isin(selected_predicted_breaker)) &
    (df['Actual_World_Record_Breaker'].isin(selected_actual_breaker))
]

if selected_nationality:
    filtered_df = filtered_df[filtered_df['Nationality'].isin(selected_nationality)]

# Apply Name Search Filter
if search_name:
    filtered_df = filtered_df[filtered_df['competitor'].str.contains(search_name, case=False, na=False)]

# Display Filtered Data
st.header("Filtered Dataset")
st.dataframe(filtered_df)

# Metrics Section
st.header("Key Metrics")

if not filtered_df.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    # Total Records
    total_records = len(filtered_df)
    col1.metric("Total Records", total_records)
    
    # Average Mark Numeric
    avg_mark = filtered_df['mark_numeric'].mean()
    col2.metric("Average Mark Numeric", f"{avg_mark:.2f}")
    
    # Average Probability
    avg_prob = filtered_df['Probability_World_Record_Breaker'].mean()
    col3.metric("Average Probability", f"{avg_prob:.4f}")
    
    # Prediction Accuracy for World Record
    # Drop rows where Actual is None (Unknown)
    acc_df = filtered_df.dropna(subset=['Actual_World_Record_Breaker'])
    if not acc_df.empty:
        accuracy = (acc_df['Predicted_World_Record_Breaker'] == acc_df['Actual_World_Record_Breaker']).mean() * 100
        col4.metric("World Record Prediction Accuracy", f"{accuracy:.2f}%")
    else:
        col4.metric("World Record Prediction Accuracy", "N/A")

# Visualizations
st.header("Visualizations")

# Histogram of Probabilities
st.subheader("Distribution of World Record Breaker Probabilities")
prob_hist = px.histogram(filtered_df, x='Probability_World_Record_Breaker', nbins=20, title="Probability Distribution")
prob_hist.update_layout(width=800, height=600)  # Increase chart size
st.plotly_chart(prob_hist, use_container_width=False)

# Bar Chart: Count of Predicted Breakers by Discipline
st.subheader("Predicted World Record Breakers by Discipline")
breaker_count = filtered_df.groupby(['Discipline', 'Predicted_World_Record_Breaker']).size().reset_index(name='Count')
breaker_bar = alt.Chart(breaker_count).mark_bar().encode(
    x='Discipline',
    y='Count',
    color='Predicted_World_Record_Breaker',
    tooltip=['Discipline', 'Predicted_World_Record_Breaker', 'Count']
).properties(
    width=800,  # Increase chart width
    height=500  # Increase chart height
).interactive()
st.altair_chart(breaker_bar, use_container_width=False)

# Scatter Plot: Mark Numeric vs Probability
st.subheader("Mark Numeric vs Probability (Colored by Actual Breaker)")
scatter = px.scatter(
    filtered_df,
    x='mark_numeric',
    y='Probability_World_Record_Breaker',
    color='Actual_World_Record_Breaker',
    hover_data=['competitor', 'Discipline', 'Nationality'],
    title="Mark vs Probability"
)
scatter.update_layout(width=800, height=600)  # Increase chart size
st.plotly_chart(scatter, use_container_width=False)

# Pie Chart: Actual vs Predicted for World Records
st.subheader("Actual vs Predicted World Record Breakers")
pie_df = filtered_df.melt(id_vars=['competitor'], value_vars=['Predicted_World_Record_Breaker', 'Actual_World_Record_Breaker'])
pie_df = pie_df[pie_df['value'].notnull()]  # Exclude None
pie_chart = px.pie(pie_df, names='variable', color='value', title="Comparison of Predicted and Actual")
pie_chart.update_layout(width=800, height=600)  # Increase chart size
st.plotly_chart(pie_chart, use_container_width=False)

# Additional Metrics for National and Personal Best
st.header("Additional Breakdowns")

col5, col6 = st.columns(2)

# National Record Accuracy
nat_acc_df = filtered_df.dropna(subset=['Actual_National_Record_Breaker'])
if not nat_acc_df.empty:
    nat_yes_count = nat_acc_df['Actual_National_Record_Breaker'].sum()
    col5.metric("Actual National Record Breakers", nat_yes_count)
else:
    col5.metric("Actual National Record Breakers", "N/A")

# Personal Best Accuracy
pb_acc_df = filtered_df.dropna(subset=['Actual_Personal_Best_Breaker'])
if not pb_acc_df.empty:
    pb_yes_count = pb_acc_df['Actual_Personal_Best_Breaker'].sum()
    col6.metric("Actual Personal Best Breakers", pb_yes_count)
else:
    col6.metric("Actual Personal Best Breakers", "N/A")

# Top Predictions Table
st.subheader("Top Predicted World Record Breakers")
top_preds = filtered_df[filtered_df['Predicted_World_Record_Breaker'] == True].sort_values('Probability_World_Record_Breaker', ascending=False).head(10)
st.table(top_preds[['competitor', 'Discipline', 'Nationality', 'mark_numeric', 'Probability_World_Record_Breaker', 'Actual_World_Record_Breaker']])