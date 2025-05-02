# Reboot-Academy-Project-2

Proyecto realizado por GuillermoDuMa, DTorrero, AzaharaG1984

PRESENTACIÓN: Miercoles 7 de Mayo

Link to dataset and Project description: [https://drive.google.com/drive/folders/1BgWcHhGl1m9VLJdfmq-VTkbdHCKCM1_j?usp=drive_link](https://tinyurl.com/yc8haw87)

---

## Project Summary

This project analyzes hotel booking data to extract insights about booking patterns, cancellation rates, and revenue (ADR). The work includes:
- Data cleaning and preprocessing
- Exploratory data analysis (EDA) in Jupyter notebooks
- Statistical analysis and visualizations
- An interactive dashboard built with Streamlit for business users

## How to Run the Project

### 1. Environment Setup

We recommend using an Anaconda environment for easy package management. You can also use `requirements.txt` with pip.

**Option A: Using Anaconda**
```bash
conda create -n hotel-bookings python=3.10
conda activate hotel-bookings
pip install -r requirements.txt
```

**Option B: Using pip**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Running the Streamlit Dashboard

Make sure you have the cleaned dataset (`hotel_bookings_clean.csv`) in the project directory.

To launch the dashboard, run:
```bash
streamlit run streamlit.py
```
This will open the interactive dashboard in your web browser.

### 3. Notebooks
- `Data_Cleaning.ipynb`: Data cleaning and preprocessing steps
- `EDA-david.ipynb`, `EDA-azahara.ipynb`, `EDA-guillermo.ipynb`: Exploratory data analysis and visualizations

---

For any questions, please contact the project authors.
