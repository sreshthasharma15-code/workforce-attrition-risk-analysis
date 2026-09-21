from pathlib import Path
import plotly.express as px
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title='Palo Alto Networks Attrition Dashboard',
    layout='wide'
)

data_path = Path(__file__).resolve().parents[1] / 'data' / 'Palo Alto Networks.csv'
df = pd.read_csv(data_path)
age_bins = [18, 25, 35, 45, 55, 65]
age_labels = ['18–25', '26–35', '36–45', '46–55', '56–65']

df['AgeGroup'] = pd.cut(
    df['Age'],
    bins=age_bins,
    labels=age_labels,
    include_lowest=True
)

tenure_bins = [-1, 2, 5, 10, float('inf')]
tenure_labels = [
    '0-2 Early tenure',
    '3-5 Developing',
    '6-10 Established',
    '11+ Long tenure'
]

df['TenureGroup'] = pd.cut(
    df['YearsAtCompany'],
    bins=tenure_bins,
    labels=tenure_labels
)

distance_bins = [-1, 5, 10, 20, float('inf')]
distance_labels = ['0-5', '6-10', '11-20', '21+']

df['DistanceGroup'] = pd.cut(
    df['DistanceFromHome'],
    bins=distance_bins,
    labels=distance_labels
)


distance_bins = [-1, 5, 10, 20, float('inf')]
distance_labels = ['0-5', '6-10', '11-20', '21+']

df['DistanceGroup'] = pd.cut(
    df['DistanceFromHome'],
    bins=distance_bins,
    labels=distance_labels
)

st.title('Workforce Attrition Patterns and Risk Hotspot Analysis')

st.sidebar.header('Filters')

department_options = ['All'] + sorted(df['Department'].unique())

selected_department = st.sidebar.selectbox(
    'Department',
    department_options
)

filtered_df = df.copy()

if selected_department != 'All':
    filtered_df = filtered_df[
        filtered_df['Department'] == selected_department
    ]

job_options=['All']+ sorted(df['JobRole'].unique())
selected_job= st.sidebar.selectbox(
    'Job Role',
    job_options
)


if selected_job != 'All':
    filtered_df = filtered_df[
        filtered_df['JobRole']==selected_job
    ]

min_tenure=int(df['YearsAtCompany'].min())
max_tenure=int(df['YearsAtCompany'].max())

selected_tenure = st.sidebar.slider(
    'Years At Company',
    min_value=min_tenure,
    max_value=max_tenure,
    value=(min_tenure,max_tenure)
)

filtered_df = filtered_df[
    filtered_df['YearsAtCompany'].between(
        selected_tenure[0],
        selected_tenure[1]
    )
]

selected_overtime = st.sidebar.selectbox(
    'Overtime',
    ['All','Yes','No']
)

if selected_overtime != 'All':
    filtered_df = filtered_df[
        filtered_df['OverTime']==selected_overtime
        ]

travel_options = ['All'] + sorted(filtered_df['BusinessTravel'].unique())

selected_travel = st.sidebar.selectbox(
    'Business Travel',
    travel_options
)

if selected_travel !='All':
    filtered_df = filtered_df[filtered_df['BusinessTravel']==selected_travel]

if filtered_df.empty:
    st.warning('No employees match the selected filters. Please adjust your filters.')
    st.stop()
st.subheader("Attrition Overview")
total_employees = filtered_df.shape[0]
exited_employees = filtered_df[filtered_df['Attrition'] == 1].shape[0]
attrition_rate = round((exited_employees / total_employees) * 100, 2)
col1,col2,col3 = st.columns(3)
col1.metric('Total employees: ',total_employees)
col2.metric('Exited employees: ',exited_employees)
col3.metric('Attrition Rate :',f'{attrition_rate}%')



attrition_labels={0: 'Retained', 1: 'Exited'}
overview_summary=(
    filtered_df['Attrition']
    .map(attrition_labels)
    .value_counts()
    .rename_axis('Status')
    .reset_index(name='Employees')
)

fig_overview=px.bar(
    overview_summary,
    x='Status',
    y='Employees',
    color='Status',
    title='Retained vs Exited Employees'
)
st.plotly_chart(fig_overview, use_container_width=True)


st.subheader("Department & Role Hotspots")
heatmap_df = filtered_df.copy()
heatmap_df['AttritionPercent'] = heatmap_df['Attrition'] * 100
fig_heatmap = px.density_heatmap(
    heatmap_df,
    x='Department',
    y='JobRole',
    z='AttritionPercent',
    histfunc='avg',
    color_continuous_scale='Reds',
    title='Department and Job Role Attrition Risk Heatmap',
    labels={'AttritionPercent': 'Attrition Rate (%)'}
)

st.plotly_chart(fig_heatmap, use_container_width=True)


st.subheader('Demographic Explorer')

age_summary = (
    filtered_df
    .groupby('AgeGroup', observed=True)['Attrition']
    .mean()
    .mul(100)
    .round(2)
    .reset_index(name='Attrition Rate (%)')
)

fig_age = px.bar(
    age_summary,
    x='AgeGroup',
    y='Attrition Rate (%)',
    color='AgeGroup',
    title='Attrition Rate by Age Group'
)



st.plotly_chart(fig_age, use_container_width=True)

gender_summary = (
    filtered_df.groupby('Gender')['Attrition']
    .mean().mul(100).round(2)
    .reset_index(name='Attrition Rate (%)')
)

education_summary = (
    filtered_df.groupby('EducationField')['Attrition']
    .mean().mul(100).round(2)
    .reset_index(name='Attrition Rate (%)')
    .sort_values('Attrition Rate (%)', ascending=False)
)

col_gender, col_education = st.columns(2)

fig_gender = px.bar(
    gender_summary,
    x='Gender',
    y='Attrition Rate (%)',
    color='Gender',
    title='Attrition Rate by Gender'
)

fig_education = px.bar(
    education_summary,
    x='Attrition Rate (%)',
    y='EducationField',
    color='EducationField',
    orientation='h',
    title='Attrition Rate by Education Field'
)
fig_education.update_layout(showlegend=False)

col_gender.plotly_chart(fig_gender, use_container_width=True)
col_education.plotly_chart(fig_education, use_container_width=True)



st.subheader('Tenure & Workload Analysis')

tenure_summary = (
    filtered_df.groupby('TenureGroup', observed=True)['Attrition']
    .mean().mul(100).round(2)
    .reset_index(name='Attrition Rate (%)')
)

fig_tenure = px.bar(
    tenure_summary,
    x='TenureGroup',
    y='Attrition Rate (%)',
    color='TenureGroup',
    title='Attrition Rate by Tenure'
)

st.plotly_chart(fig_tenure, use_container_width=True)

overtime_summary = (
    filtered_df.groupby('OverTime')['Attrition']
    .mean().mul(100).round(2)
    .reset_index(name='Attrition Rate (%)')
)

travel_summary = (
    filtered_df.groupby('BusinessTravel')['Attrition']
    .mean().mul(100).round(2)
    .reset_index(name='Attrition Rate (%)')
    .sort_values('Attrition Rate (%)', ascending=False)
)

col_overtime, col_travel = st.columns(2)

fig_overtime = px.bar(
    overtime_summary,
    x='OverTime',
    y='Attrition Rate (%)',
    color='OverTime',
    title='Attrition Rate by Overtime'
)

fig_travel = px.bar(
    travel_summary,
    x='BusinessTravel',
    y='Attrition Rate (%)',
    color='BusinessTravel',
    title='Attrition Rate by Business Travel'
)


col_overtime.plotly_chart(fig_overtime, use_container_width=True)
col_travel.plotly_chart(fig_travel, use_container_width=True)

distance_summary = (
    filtered_df.groupby('DistanceGroup', observed=True)['Attrition']
    .mean().mul(100).round(2)
    .reset_index(name='Attrition Rate (%)')
)
fig_distance = px.bar(
    distance_summary,
    x='DistanceGroup',
    y='Attrition Rate (%)',
    color='DistanceGroup',
    title='Attrition Rate by Distance from Home'
)
st.plotly_chart(fig_distance, use_container_width=True)
with st.expander("View Filtered Employee Data"):
    st.dataframe(filtered_df, use_container_width=True)