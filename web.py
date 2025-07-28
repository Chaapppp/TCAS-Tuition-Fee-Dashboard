import json
import os
import pandas as pd
import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
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

# --- Prepare Data for Dash Tables ---
def prepare_table_data(dataframe):

    df_copy = dataframe.copy() 

    df_copy['ค่าใช้จ่ายต่อภาคการศึกษา'] = pd.to_numeric(df_copy['ค่าใช้จ่ายต่อภาคการศึกษา'], errors='coerce').fillna(0)

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
        'ค่าใช้จ่ายต่อภาคการศึกษา',
        'Admission Rounds'
    ]].copy()

    display_df.rename(columns={
        'university': 'University',
        'faculty': 'Faculty',
        'ค่าใช้จ่ายต่อภาคการศึกษา': 'Tuition Fees per Semester (THB)'
    }, inplace=True)

    return display_df.to_dict('records')

ai_programs_df = df[df['search_term'].str.contains('ปัญญาประดิษฐ์', na=False)].copy()
coe_programs_df = df[df['search_term'].str.contains('วิศวกรรมคอมพิวเตอร์', na=False)].copy()

initial_ai_data = prepare_table_data(ai_programs_df)
initial_coe_data = prepare_table_data(coe_programs_df)

table_columns = [
    {"name": "Program Title", "id": "Program Title"},
    {"name": "University", "id": "University"},
    {"name": "Faculty", "id": "Faculty"},
    {"name": "Tuition Fees per Semester (THB)", "id": "Tuition Fees per Semester (THB)", "type": "numeric"},
    {"name": "Admission Rounds", "id": "Admission Rounds"},
]

# --- Dash App Layout ---
app.layout = dbc.Container([
    html.H1("🎓 University Program Dashboard 🎓", className="text-center my-4 text-primary"),
    html.P("Insights for your upcoming university journey in AI and Computer Engineering.", className="text-center text-muted mb-5"),

    dbc.Spinner(children=[
        html.Section([
            html.H2(html.B("Overview"), className="section-title"),
            dbc.Row([
                dbc.Col(html.Label("Filter by Semester Cost:", className="lead"), width="auto"),
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
                dbc.Col(html.Label("Filter by Program Type:", className="lead"), width="auto"),
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
            dash_table.DataTable(
                id='cost-programs-table',
                columns=table_columns,
                data=prepare_table_data(df), 
                style_table={'overflowX': 'auto', 'borderRadius': '0.75rem', 'boxShadow': '0 2px 10px rgba(0,0,0,0.03)'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '0.75rem 1rem',
                    'height': 'auto',
                },
                style_header={
                    'backgroundColor': '#edf2f7',
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
                        'width': '500px', # Fixed width as requested
                    },
                    {
                        'if': {'column_id': 'Program Title'},
                        'whiteSpace': 'normal',
                        'textAlign': 'left',
                        'width': '400px', # Fixed width as requested
                    }
                ],
                page_size=10,
                filter_action="native",
                sort_action="native",
            )
        ], className="card p-4 mb-5"), 

 
    ], color="primary", type="grow", fullscreen=False)
], fluid=True, className="py-4")

# --- Callbacks ---
@app.callback(
    Output('cost-programs-table', 'data'),
    Input('cost-range-dropdown', 'value'),
    Input('cost-program-type-dropdown', 'value')
)
def update_cost_table(selected_range, selected_type):
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

    return prepare_table_data(filtered_df)

if __name__ == '__main__':
    app.run(debug=True)