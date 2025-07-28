# TCAS University Program Dashboard [Computer & AI Engineering]

This project presents a Dash web application designed to visualize pre-processed tuition fee data for Computer Engineering and Artificial Intelligence Engineering programs offered by Thai universities.

## Project Overview
This Dash application serves as an interactive dashboard to help prospective university students and parents make informed decisions about higher education in Thailand. It visualizes tuition fees and admission details for Computer Engineering and AI programs, offering filtering capabilities and a clear, responsive interface.

## Features
- Program Costs Overview: Displays a comprehensive table of university programs.

- Interactive Filtering:

  - Semester Cost Range: Filter programs by specific tuition fee ranges per semester.

  - Program Type: Isolate results to show only Artificial Intelligence Engineering, Computer Engineering (CoE), or all relevant programs.

  - Program Language Type: Filter programs by courses' language type (e.g., "ภาษาไทย ปกติ" or "นานาชาติ").
  
- Responsive Data Tables: dash_table.DataTable ensures that program titles wrap for full visibility and admission round details are presented clearly on separate lines within cells.

- Dynamic Visualizations:

  - Tuition Fee Distribution by Program Type: A histogram showing how tuition fees are distributed, separated by AI and CoE programs with consistent coloring.

  - Average Semester Tuition by University and Program Type: A bar chart comparing average tuition fees across universities, broken down by AI and CoE programs with consistent coloring.

## Data Processing

- Data Scraping: Course information is extracted from [course.mytcas.com](https://course.mytcas.com)

- Data Refinement: The collected dataset is cleaned and duplicate entries are removed to ensure data integrity.

- Targeted Filtering: Only programs relevant to Computer Engineering and Artificial Intelligence Engineering are selected for analysis.

- Data Normalization: Normalizing tuition fees, including conversion to a per-semester basis where necessary.

## Setup & Installation
To set up and run this application locally, please follow these steps:

### Prerequisites
- Python 3.7+

- pip (Python package installer)

### 1. Clone the repository
```bash
git clone <repo-url>
```

### 2. Create a virtual environment
```bash
python -m venv venv
```

### 3. Install requirement.txt
```bash
pip install -r requirement.txt
```

### 4. Install Playwright Browsers
If your data processing involves web scraping with Playwright, you'll need to install the necessary browser binaries:

```bash
playwright install
```

### 5. Run the Application
From your project directory in the terminal, run the web.py script:

```bash
python web.py
```

### 6. Access the Dashboard
Open your web browser and navigate to the following address:

```bash
http://127.0.0.1:8050/
```

The dashboard will load, displaying the university program data with interactive filters.

## Usage
- Use the various dropdown menus to narrow down the displayed programs based on your criteria.

- The data table allows native filtering (type into the search boxes below column headers) and sorting (click on column headers).

- Observe the graphs for insights into tuition distribution and average costs per university. All dynamic charts update based on your selected filters.
