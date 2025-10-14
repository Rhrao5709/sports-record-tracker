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
# Add predicted columns if they exist in your dataset; if not, comment out those not present
# Adjust these based on actual column names in your dataset
if 'Predicted_National_Record_Breaker' in df.columns:
    bool_columns.append('Predicted_National_Record_Breaker')
if 'Predicted_Personal_Best_Breaker' in df.columns:
    bool_columns.append('Predicted_Personal_Best_Breaker')

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

# Apply Filters
filtered_df = df[
    (df['Sex'].isin(selected_sex)) &
    (df['Discipline'].isin(selected_discipline))
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
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Total Records
    total_records = len(filtered_df)
    col1.metric("Total Records", total_records)
    
    # Average Mark Numeric
    avg_mark = filtered_df['mark_numeric'].mean()
    col2.metric("Average Mark Numeric", f"{avg_mark:.2f}")
    
    # Average Probability
    avg_prob = filtered_df['Probability_World_Record_Breaker'].mean()
    col3.metric("Average Probability (World Record)", f"{avg_prob:.4f}")
    
    # Predicted World Record Breakers
    pred_world_count = filtered_df['Predicted_World_Record_Breaker'].sum(skipna=True)
    col4.metric("Predicted World Record Breakers", pred_world_count)
    
    # Actual World Record Breakers
    actual_world_count = filtered_df['Actual_World_Record_Breaker'].sum(skipna=True)
    col5.metric("Actual World Record Breakers", actual_world_count)

# Visualizations for World Records
st.header("World Record Visualizations")

# Histogram of Probabilities
st.subheader("Distribution of World Record Breaker Probabilities")
prob_hist = px.histogram(filtered_df, x='Probability_World_Record_Breaker', nbins=20, title="Probability Distribution")
prob_hist.update_layout(width=800, height=600)
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
    width=800,
    height=500
).interactive()
st.altair_chart(breaker_bar, use_container_width=False)

# Scatter Plot: Mark Numeric vs Probability
st.subheader("Mark Numeric vs Probability (Colored by Actual World Breaker)")
scatter = px.scatter(
    filtered_df,
    x='mark_numeric',
    y='Probability_World_Record_Breaker',
    color='Actual_World_Record_Breaker',
    hover_data=['competitor', 'Discipline', 'Nationality'],
    title="Mark vs Probability (World)"
)
scatter.update_layout(width=800, height=600)
st.plotly_chart(scatter, use_container_width=False)

# Pie Chart: Actual vs Predicted for World Records
st.subheader("Actual vs Predicted World Record Breakers")
pie_df = filtered_df.melt(id_vars=['competitor'], value_vars=['Predicted_World_Record_Breaker', 'Actual_World_Record_Breaker'])
pie_df = pie_df[pie_df['value'].notnull()]  # Exclude None
pie_chart = px.pie(pie_df, names='variable', color='value', title="Comparison of Predicted and Actual (World)")
pie_chart.update_layout(width=800, height=600)
st.plotly_chart(pie_chart, use_container_width=False)

# National Record Visualizations
st.header("National Record Visualizations")

# Bar Chart: Count of Actual National Breakers by Discipline
st.subheader("Actual National Record Breakers by Discipline")
nat_breaker_count = filtered_df.groupby(['Discipline', 'Actual_National_Record_Breaker']).size().reset_index(name='Count')
nat_bar = alt.Chart(nat_breaker_count).mark_bar().encode(
    x='Discipline',
    y='Count',
    color='Actual_National_Record_Breaker',
    tooltip=['Discipline', 'Actual_National_Record_Breaker', 'Count']
).properties(
    width=800,
    height=500
).interactive()
st.altair_chart(nat_bar, use_container_width=False)

# Scatter Plot: Mark Numeric vs Probability (Colored by Actual National)
st.subheader("Mark Numeric vs Probability (Colored by Actual National Breaker)")
nat_scatter = px.scatter(
    filtered_df,
    x='mark_numeric',
    y='Probability_World_Record_Breaker',
    color='Actual_National_Record_Breaker',
    hover_data=['competitor', 'Discipline', 'Nationality'],
    title="Mark vs Probability (National)"
)
nat_scatter.update_layout(width=800, height=600)
st.plotly_chart(nat_scatter, use_container_width=False)

# Pie Chart: Distribution of Actual National Record Breakers
st.subheader("Distribution of Actual National Record Breakers")
nat_pie_df = filtered_df['Actual_National_Record_Breaker'].value_counts().reset_index()
nat_pie_df.columns = ['Actual_National_Record_Breaker', 'Count']
nat_pie = px.pie(nat_pie_df, names='Actual_National_Record_Breaker', values='Count', title="Actual National Record Breakers Distribution")
nat_pie.update_layout(width=800, height=600)
st.plotly_chart(nat_pie, use_container_width=False)

# Personal Best Visualizations
st.header("Personal Best Visualizations")

# Bar Chart: Count of Actual Personal Best by Discipline
st.subheader("Actual Personal Best Breakers by Discipline")
pb_breaker_count = filtered_df.groupby(['Discipline', 'Actual_Personal_Best_Breaker']).size().reset_index(name='Count')
pb_bar = alt.Chart(pb_breaker_count).mark_bar().encode(
    x='Discipline',
    y='Count',
    color='Actual_Personal_Best_Breaker',
    tooltip=['Discipline', 'Actual_Personal_Best_Breaker', 'Count']
).properties(
    width=800,
    height=500
).interactive()
st.altair_chart(pb_bar, use_container_width=False)

# Scatter Plot: Mark Numeric vs Probability (Colored by Actual Personal Best)
st.subheader("Mark Numeric vs Probability (Colored by Actual Personal Best Breaker)")
pb_scatter = px.scatter(
    filtered_df,
    x='mark_numeric',
    y='Probability_World_Record_Breaker',
    color='Actual_Personal_Best_Breaker',
    hover_data=['competitor', 'Discipline', 'Nationality'],
    title="Mark vs Probability (Personal Best)"
)
pb_scatter.update_layout(width=800, height=600)
st.plotly_chart(pb_scatter, use_container_width=False)

# Pie Chart: Distribution of Actual Personal Best Breakers
st.subheader("Distribution of Actual Personal Best Breakers")
pb_pie_df = filtered_df['Actual_Personal_Best_Breaker'].value_counts().reset_index()
pb_pie_df.columns = ['Actual_Personal_Best_Breaker', 'Count']
pb_pie = px.pie(pb_pie_df, names='Actual_Personal_Best_Breaker', values='Count', title="Actual Personal Best Breakers Distribution")
pb_pie.update_layout(width=800, height=600)
st.plotly_chart(pb_pie, use_container_width=False)

# Additional Breakdowns
st.header("Additional Breakdowns")

col6, col7, col8, col9 = st.columns(4)

# Predicted National Record Breakers
if 'Predicted_National_Record_Breaker' in filtered_df.columns:
    pred_nat_count = filtered_df['Predicted_National_Record_Breaker'].sum(skipna=True)
    col6.metric("Predicted National Record Breakers", pred_nat_count)
else:
    col6.metric("Predicted National Record Breakers", "N/A")

# Actual National Record Breakers
nat_acc_df = filtered_df.dropna(subset=['Actual_National_Record_Breaker'])
if not nat_acc_df.empty:
    nat_yes_count = nat_acc_df['Actual_National_Record_Breaker'].sum()
    col7.metric("Actual National Record Breakers", nat_yes_count)
else:
    col7.metric("Actual National Record Breakers", "N/A")

# Predicted Personal Best Breakers
if 'Predicted_Personal_Best_Breaker' in filtered_df.columns:
    pred_pb_count = filtered_df['Predicted_Personal_Best_Breaker'].sum(skipna=True)
    col8.metric("Predicted Personal Best Breakers", pred_pb_count)
else:
    col8.metric("Predicted Personal Best Breakers", "N/A")

# Actual Personal Best Breakers
pb_acc_df = filtered_df.dropna(subset=['Actual_Personal_Best_Breaker'])
if not pb_acc_df.empty:
    pb_yes_count = pb_acc_df['Actual_Personal_Best_Breaker'].sum()
    col9.metric("Actual Personal Best Breakers", pb_yes_count)
else:
    col9.metric("Actual Personal Best Breakers", "N/A")

# Top Predictions Table
st.subheader("Top Predicted World Record Breakers")
top_preds = filtered_df[filtered_df['Predicted_World_Record_Breaker'] == True].sort_values('Probability_World_Record_Breaker', ascending=False).head(10)
st.table(top_preds[['competitor', 'Discipline', 'Nationality', 'mark_numeric', 'Probability_World_Record_Breaker', 'Actual_World_Record_Breaker']])

# Top Actual National Record Breakers (sorted by mark_numeric ascending, assuming lower is better)
st.subheader("Top Actual National Record Breakers")
top_nat = filtered_df[filtered_df['Actual_National_Record_Breaker'] == True].sort_values('mark_numeric', ascending=True).head(10)
st.table(top_nat[['competitor', 'Discipline', 'Nationality', 'mark_numeric', 'Actual_National_Record_Breaker']])

# Top Actual Personal Best Breakers (sorted by mark_numeric ascending)
st.subheader("Top Actual Personal Best Breakers")
top_pb = filtered_df[filtered_df['Actual_Personal_Best_Breaker'] == True].sort_values('mark_numeric', ascending=True).head(10)
st.table(top_pb[['competitor', 'Discipline', 'Nationality', 'mark_numeric', 'Actual_Personal_Best_Breaker']])

top_10_men_national_record_breakers = pd.read_csv("top_10_men_national_record_breakers.csv")
top_10_men_personal_best_breakers = pd.read_csv("top_10_men_personal_best_breakers.csv")
top_10_men_world_record_breakers = pd.read_csv("top_10_men_world_record_breakers.csv")
top_10_women_national_record_breakers = pd.read_csv("top_10_women_national_record_breakers.csv")
top_10_women_personal_best_breakers = pd.read_csv("top_10_women_personal_best_breakers.csv")
top_10_women_world_record_breakers = pd.read_csv("top_10_women_world_record_breakers.csv")

# Display Men's Tables
st.subheader("Men's National Record Breakers")
st.dataframe(top_10_men_national_record_breakers)

st.subheader("Men's Personal Best Breakers")
st.dataframe(top_10_men_personal_best_breakers)

st.subheader("Men's World Record Breakers")
st.dataframe(top_10_men_world_record_breakers)

# Display Women's Tables
st.subheader("Women's National Record Breakers")
st.dataframe(top_10_women_national_record_breakers)

st.subheader("Women's Personal Best Breakers")
st.dataframe(top_10_women_personal_best_breakers)

st.subheader("Women's World Record Breakers")
st.dataframe(top_10_women_world_record_breakers)