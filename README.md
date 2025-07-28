# TCAS University Program Dashboard [Computer & AI Engineering]
This project presents a Dash web application designed to visualize pre-processed tuition fee data for Computer Engineering and Artificial Intelligence Engineering programs offered by Thai universities. The dashboard focuses on providing an executive summary, allowing users to easily compare tuition costs and explore programs based on various filters.

## Project Overview
This Dash application serves as an interactive dashboard to help prospective university students and parents make informed decisions about higher education in Thailand. It visualizes tuition fees and admission details for Computer Engineering and AI programs, offering filtering capabilities and a clear, responsive interface.

## Features
- Program Costs Overview: Displays a comprehensive table of university programs.

- Interactive Filtering:

  - Semester Cost Range: Filter programs by specific tuition fee ranges per semester.

  - Program Type: Isolate results to show only Artificial Intelligence Engineering, Computer Engineering (CoE), or all relevant programs.
  
  - Responsive Data Tables: dash_table.DataTable ensures that program titles wrap for full visibility and admission round details are presented clearly on separate lines within cells.


## Data Source & Processing
The data for this dashboard is sourced from a pre-processed JSON file: course_semester_tuition.json. This file contains structured information about university programs, including tuition fees, university names, faculties, program titles, and admission round details.

## Setup & Installation
To set up and run this application locally, please follow these steps:

### Prerequisites
- Python 3.7+

- pip (Python package installer)

### 1. Clone the repository
```git clone <repo-url>```

### 2. Create a virtual environment
```python -m venv venv```

### 3. Install requirement.txt
```pip install -r requirement.txt```

### 4. Run the Application
From your project directory in the terminal, run the web.py script:

```python web.py```

### 5. Access the Dashboard
Open your web browser and navigate to the following address:

```http://127.0.0.1:8050/```

The dashboard will load, displaying the university program data with interactive filters.


**Data Source**: [Thai University Central Admission System (TCAS)](https://course.mytcas.com)