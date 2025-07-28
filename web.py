import json
import os
import pandas as pd
import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])
server = app.server

DATA_FILE_PATH = 'data/course_semester_tuition.json'

# --- Load Data ---
all_programs_data = []
try:
    full_data_path = os.path.join(os.path.dirname(__file__), DATA_FILE_PATH)
    with open(full_data_path, 'r', encoding='utf-8') as f:
        all_programs_data = json.load(f)
    print(f"Data loaded successfully from {full_data_path}. Found {len(all_programs_data)} programs.")
except FileNotFoundError:
    print(f"Error: Data file '{full_data_path}' not found.")
    print(f"Please ensure '{DATA_FILE_PATH}' is located relative to 'web.py'.")
    exit()
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from '{full_data_path}'. Check file format.")
    exit()

df = pd.DataFrame(all_programs_data)

df.rename(columns={'ค่าใช้จ่ายต่อภาคการศึกษา': 'Semester Cost (THB)'}, inplace=True)
df['Semester Cost (THB)'] = pd.to_numeric(df['Semester Cost (THB)'], errors='coerce').fillna(0)
program_types = df['details'].apply(lambda x: x.get('ประเภทหลักสูตร') if isinstance(x, dict) else None).dropna().unique()
program_type_options = [{'label': 'All Types', 'value': 'all'}] + \
                       [{'label': pt, 'value': pt} for pt in sorted(program_types)]

# --- Prepare Data for Dash Tables ---
def prepare_table_data(dataframe):

    df_copy = dataframe.copy() 

    def get_admission_text(details):
        if not isinstance(details, dict):
            return 'N/A'
        rounds = []
        if details.get('รอบ 1 Portfolio'): rounds.append(f"Portfolio: {details['รอบ 1 Portfolio']}")
        if details.get('รอบ 2 Quota'): rounds.append(f"Quota: {details['รอบ 2 Quota']}")
        if details.get('รอบ 3 Admission'): rounds.append(f"Admission: {details['รอบ 3 Admission']}")
        if details.get('รอบ 4 Direct Admission'): rounds.append(f"Direct: {details['รอบ 4 Direct Admission']}")
        return '\n'.join(rounds) if rounds else 'N/A' # Keep joining with \n

    df_copy['Admission Rounds'] = df_copy['details'].apply(get_admission_text)

    display_df = df_copy[[
        'Program Title',
        'university',
        'faculty',
        'Semester Cost (THB)', 
        'Admission Rounds'
    ]].copy()

    display_df.rename(columns={
        'university': 'University',
        'faculty': 'Faculty',
    }, inplace=True)

    return display_df.to_dict('records')

ai_programs_df = df[df['search_term'].str.contains('ปัญญาประดิษฐ์', na=False)].copy()
coe_programs_df = df[df['search_term'].str.contains('วิศวกรรมคอมพิวเตอร์', na=False)].copy()

initial_ai_data = prepare_table_data(ai_programs_df)
initial_coe_data = prepare_table_data(coe_programs_df)

program_types = df['details'].apply(lambda x: x.get('ประเภทหลักสูตร') if isinstance(x, dict) else None).dropna().unique()
program_type_options = [{'label': 'All Types', 'value': 'all'}] + \
                       [{'label': pt, 'value': pt} for pt in sorted(program_types)]

table_columns = [
    {"name": "Program Title", "id": "Program Title"},
    {"name": "University", "id": "University"},
    {"name": "Faculty", "id": "Faculty"},
    {"name": "Tuition Fees per Semester (THB)", "id": "Semester Cost (THB)", "type": "numeric"},
    {"name": "Admission Rounds", "id": "Admission Rounds"},
]

CUSTOM_PROGRAM_TYPE_COLORS = {
    'วิศวกรรมปัญญาประดิษฐ์': "#c1edff",  
    'วิศวกรรมคอมพิวเตอร์': "#F16C55"   
}

# --- Dash App Layout ---
app.layout = dbc.Container([
    html.H1("🎓 University Program Dashboard 🎓", className="text-center my-4 text-primary"),
    html.P("Insights for your upcoming university journey in AI and Computer Engineering.", className="text-center text-muted mb-5"),

    dbc.Spinner(children=[
        html.Section([
            html.H2(html.B("Overview"), className="section-title"),
            dbc.Row([
                dbc.Col(html.Label(html.B("Filter by Semester Cost:"), className="lead"), width="auto"),
                dbc.Col(dcc.Dropdown(
                    id='cost-range-dropdown',
                    options=[
                        {'label': 'All Ranges', 'value': 'all'},
                        {'label': 'Below 50,000 THB', 'value': '0-50000'},
                        {'label': '50,001 - 100,000 THB', 'value': '50001-100000'},
                        {'label': '100,001 - 200,000 THB', 'value': '100001-200000'},
                        {'label': 'Above 200,000 THB', 'value': '200001-9999999'},
                    ],
                    value='all',
                    clearable=False,
                ), width=12),
            ], className="mb-4 align-items-center"),

            dbc.Row([
                dbc.Col(html.Label(html.B("Filter by Program Type:"), className="lead"), width="auto"),
                dbc.Col(dcc.Dropdown(
                    id='cost-program-type-dropdown', 
                    options=[
                        {'label': 'All Programs', 'value': 'all'},
                        {'label': 'Artificial Intelligence Engineering', 'value': 'ai'},
                        {'label': 'Computer Engineering (CoE)', 'value': 'coe'},
                    ],
                    value='all',
                    clearable=False,
                ), width=12),
            ], className="mb-4 align-items-center"),

            dbc.Row([
                dbc.Col(html.Label(html.B("Filter by Program Language Type:"), className="lead"), width="auto"),
                dbc.Col(dcc.Dropdown(
                    id='language-type-dropdown', 
                    options=program_type_options, 
                    value='all',
                    clearable=False,
                ), width=12),
            ], className="mb-4 align-items-center"),

            dash_table.DataTable(
                id='cost-programs-table',
                columns=table_columns,
                data=prepare_table_data(df), 
                style_table={'overflowX': 'auto', 'borderRadius': '0.75rem', 'boxShadow': '0 2px 10px rgba(0,0,0,0.03)'},
                style_cell={
                    'textAlign': 'center',
                    'padding': '0.75rem 1rem',
                    'height': 'auto',
                },
                style_header={
                    'backgroundColor': "#f1f9fc",
                    'fontWeight': 'bold',
                    'color': '#4a5568',
                    'textTransform': 'uppercase',
                    'fontSize': '0.875rem',
                    'borderBottom': '1px solid #e2e8f0',
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f8fafc'
                    },
                    {
                        'if': {'column_id': 'Admission Rounds'},
                        'whiteSpace': 'pre-wrap',
                        'textAlign': 'left',
                        'width': '500px', 
                    },
                    {
                        'if': {'column_id': 'Program Title'},
                        'whiteSpace': 'normal',
                        'textAlign': 'left',
                        'width': '400px', 
                    }
                ],
                page_size=10,
                filter_action="native",
                sort_action="native",
            ),

            html.Div([
                html.H3(html.B("Visual Insights"), className="section-title"),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='tuition-distribution-graph'), md=12), 
                    dbc.Col(dcc.Graph(id='avg-tuition-university-graph'), md=12), 
                ]),
            ], className="card p-4 mb-4"), 

        ], className="card p-4 mb-5"), 
 
    ], color="primary", type="grow", fullscreen=False)
], fluid=True, className="py-4", style={'backgroundColor': '#e4f7fe'})

@app.callback(
    Output('cost-programs-table', 'data'),
    Output('tuition-distribution-graph', 'figure'),
    Output('avg-tuition-university-graph', 'figure'),
    Input('cost-range-dropdown', 'value'),
    Input('cost-program-type-dropdown', 'value'),
    Input('language-type-dropdown', 'value')   
)
def update_cost_table(selected_range, selected_type, selected_language_type):
    filtered_df = df.copy() 

    if selected_range != 'all':
        min_cost, max_cost = map(int, selected_range.split('-'))
        filtered_df = filtered_df[
            (filtered_df['ค่าใช้จ่ายต่อภาคการศึกษา'] >= min_cost) &
            (filtered_df['ค่าใช้จ่ายต่อภาคการศึกษา'] <= max_cost)
        ]

    if selected_type == 'ai':
        filtered_df = filtered_df[filtered_df['search_term'].str.contains('ปัญญาประดิษฐ์', na=False)]
    elif selected_type == 'coe':
        filtered_df = filtered_df[filtered_df['search_term'].str.contains('วิศวกรรมคอมพิวเตอร์', na=False)]
    if selected_language_type != 'all':
        filtered_df = filtered_df[filtered_df['details'].apply(lambda x: x.get('ประเภทหลักสูตร') == selected_language_type if isinstance(x, dict) else False)]

    # 1. Tuition Fee Distribution (Histogram)
    tuition_dist_fig = px.histogram(
        filtered_df,
        x='Semester Cost (THB)',
        nbins=20,
        title='<b>Tuition Fee Distribution by Program Type (AI/CoE)</b>',
        labels={'Semester Cost (THB)': 'Semester Cost (THB)', 'search_term': 'Program Type (AI/CoE)'},
        color='search_term',
        color_discrete_sequence=px.colors.qualitative.Dark24,
        color_discrete_map=CUSTOM_PROGRAM_TYPE_COLORS
    )
    tuition_dist_fig.update_layout(
        plot_bgcolor="#f8f7f7",
        paper_bgcolor="#f8f7f7",
        font_color='#4a5568',
        xaxis_title="Semester Cost (THB)",
        yaxis_title="Number of Programs"
    )

    # 2. Average Tuition Fee by University (Bar Chart)
    avg_tuition_by_uni_type = filtered_df.groupby(['university', 'search_term'])['Semester Cost (THB)'].mean().reset_index()
    avg_tuition_by_uni_type = avg_tuition_by_uni_type.sort_values(by='Semester Cost (THB)', ascending=False)
    avg_tuition_uni_fig = px.bar(
        avg_tuition_by_uni_type,
        x='university',
        y='Semester Cost (THB)',
        color='search_term',
        title='<b>Average Semester Tuition by University and Program Type (AI/CoE)</b>', 
        labels={'Semester Cost (THB)': 'Average Semester Cost (THB)', 'university': 'University', 'search_term': 'Program Type (AI/CoE)'}, 
        barmode='group',
        color_discrete_sequence=px.colors.qualitative.Dark24,
        color_discrete_map=CUSTOM_PROGRAM_TYPE_COLORS
    )
    avg_tuition_uni_fig.update_layout(
        plot_bgcolor="#f8f7f7",
        paper_bgcolor="#f8f7f7",
        font_color='#4a5568',
        xaxis_title="University",
        yaxis_title="Average Semester Cost (THB)"
    )

    return prepare_table_data(filtered_df), tuition_dist_fig, avg_tuition_uni_fig

if __name__ == '__main__':
    app.run(debug=True)