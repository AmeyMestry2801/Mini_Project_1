# -*- coding: utf-8 -*-
"""Amey_miniproj23.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1P-fznLSrPoWFqzUWmfoICwPgd1V63Zhp
"""

import pandas as pd
import sqlite3
import os
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("train.csv")
print(df.shape)
df.info()
df.head()

df.isna().sum()

def create_connection(db_file, delete_db=False):
    if delete_db and os.path.exists(db_file):
        os.remove(db_file)

    conn = None
    try:
        conn = sqlite3.connect(db_file)
        conn.execute("PRAGMA foreign_keys = 1")
    except sqlite3.Error as e:
        print(e)
    return conn



def create_table(conn, create_table_sql, drop_table_name=None):
    if drop_table_name:
        try:
            conn.execute(f"DROP TABLE IF EXISTS {drop_table_name}")
        except sqlite3.Error as e:
            print(e)

    try:
        conn.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

def create_lookup_table(column_name, table_name, db_filename, data_filename):
    import sqlite3

    unique_values = set()
    with open(data_filename, "r", encoding="utf-8") as f:
        header = f.readline().strip().split(",")
        idx = header.index(column_name)
        for line in f:
            row = line.strip().split(",")
            if len(row) <= idx:
                continue
            value = row[idx].strip()
            if value:  # avoid blanks
                unique_values.add(value)

    conn = create_connection(db_filename)
    create_table(conn, f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value TEXT UNIQUE
        );
    """, drop_table_name=table_name)

    for val in unique_values:
        try:
            conn.execute(f"INSERT INTO {table_name} (value) VALUES (?)", (val,))
        except sqlite3.IntegrityError:
            pass  # Skip duplicates safely

    conn.commit()
    conn.close()

create_lookup_table("Gender", "Gender", "normalized_employee.db", "train.csv")
create_lookup_table("Job Role", "JobRole", "normalized_employee.db", "train.csv")
create_lookup_table("Work-Life Balance", "WorkLifeBalance", "normalized_employee.db", "train.csv")
create_lookup_table("Job Satisfaction", "JobSatisfaction", "normalized_employee.db", "train.csv")
create_lookup_table("Performance Rating", "PerformanceRating", "normalized_employee.db", "train.csv")
create_lookup_table("Education Level", "EducationLevel", "normalized_employee.db", "train.csv")
create_lookup_table("Marital Status", "MaritalStatus", "normalized_employee.db", "train.csv")
create_lookup_table("Job Level", "JobLevel", "normalized_employee.db", "train.csv")
create_lookup_table("Company Size", "CompanySize", "normalized_employee.db", "train.csv")
create_lookup_table("Attrition", "AttritionStatus", "normalized_employee.db", "train.csv")

def build_all_id_dicts(db_filename):
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    lookup_tables = [
        "Gender", "JobRole", "WorkLifeBalance", "JobSatisfaction",
        "PerformanceRating", "EducationLevel", "MaritalStatus",
        "JobLevel", "CompanySize", "AttritionStatus"
    ]

    id_dicts = {}

    for table in lookup_tables:
        cursor.execute(f"SELECT id, value FROM {table}")
        id_dicts[table] = {value: id_ for id_, value in cursor.fetchall()}

    conn.close()
    return id_dicts

id_dicts = build_all_id_dicts("normalized_employee.db")

def create_employee_table(db_filename, data_filename, id_dicts):
    conn = create_connection(db_filename)
    create_table(conn, """
        CREATE TABLE IF NOT EXISTS Employee (
            employee_id INTEGER PRIMARY KEY,
            age INTEGER,
            years_at_company INTEGER,
            monthly_income INTEGER,
            number_of_promotions INTEGER,
            distance_from_home INTEGER,
            number_of_dependents INTEGER,
            company_tenure INTEGER,
            gender_id INTEGER,
            job_role_id INTEGER,
            wlb_id INTEGER,
            satisfaction_id INTEGER,
            rating_id INTEGER,
            education_level_id INTEGER,
            marital_status_id INTEGER,
            job_level_id INTEGER,
            company_size_id INTEGER,
            attrition_status_id INTEGER,
            FOREIGN KEY (gender_id) REFERENCES Gender(id),
            FOREIGN KEY (job_role_id) REFERENCES JobRole(id),
            FOREIGN KEY (wlb_id) REFERENCES WorkLifeBalance(id),
            FOREIGN KEY (satisfaction_id) REFERENCES JobSatisfaction(id),
            FOREIGN KEY (rating_id) REFERENCES PerformanceRating(id),
            FOREIGN KEY (education_level_id) REFERENCES EducationLevel(id),
            FOREIGN KEY (marital_status_id) REFERENCES MaritalStatus(id),
            FOREIGN KEY (job_level_id) REFERENCES JobLevel(id),
            FOREIGN KEY (company_size_id) REFERENCES CompanySize(id),
            FOREIGN KEY (attrition_status_id) REFERENCES AttritionStatus(id)
        );
    """, drop_table_name="Employee")

    with open(data_filename, "r", encoding="utf-8") as f:
        header = f.readline().strip().split(",")
        idx = {col: header.index(col) for col in header}

        for line in f:
            row = line.strip().split(",")
            try:
                values = (
                    int(row[idx["Employee ID"]]),
                    int(row[idx["Age"]]),
                    int(row[idx["Years at Company"]]),
                    int(row[idx["Monthly Income"]]),
                    int(row[idx["Number of Promotions"]]),
                    int(row[idx["Distance from Home"]]),
                    int(row[idx["Number of Dependents"]]),
                    int(row[idx["Company Tenure"]]),
                    id_dicts["Gender"][row[idx["Gender"]]],
                    id_dicts["JobRole"][row[idx["Job Role"]]],
                    id_dicts["WorkLifeBalance"][row[idx["Work-Life Balance"]]],
                    id_dicts["JobSatisfaction"][row[idx["Job Satisfaction"]]],
                    id_dicts["PerformanceRating"][row[idx["Performance Rating"]]],
                    id_dicts["EducationLevel"][row[idx["Education Level"]]],
                    id_dicts["MaritalStatus"][row[idx["Marital Status"]]],
                    id_dicts["JobLevel"][row[idx["Job Level"]]],
                    id_dicts["CompanySize"][row[idx["Company Size"]]],
                    id_dicts["AttritionStatus"][row[idx["Attrition"]]]
                )
                conn.execute("""
                    INSERT INTO Employee VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, values)
            except Exception as e:
                print("Skipping row due to error:", e)

    conn.commit()
    conn.close()

create_employee_table("normalized_employee.db", "train.csv", id_dicts)

conn = sqlite3.connect("normalized_employee.db")
df = pd.read_sql_query("SELECT * FROM Employee LIMIT 5", conn)
display(df)
conn.close()

conn = sqlite3.connect("normalized_employee.db")

df_csv = pd.read_csv("train.csv")

"""1: Which job roles are most at risk for employee attrition?"""

query_q1 = """
SELECT jr.value AS job_role,
       a.value AS attrition,
       COUNT(*) AS count
FROM Employee e
JOIN JobRole jr ON e.job_role_id = jr.id
JOIN AttritionStatus a ON e.attrition_status_id = a.id
GROUP BY jr.value, a.value
ORDER BY jr.value, a.value;
"""

pd.read_sql_query(query_q1, conn)

"""2: How does job satisfaction relate to attrition?"""

query_q2 = """
SELECT js.value AS job_satisfaction,
       a.value AS attrition,
       COUNT(*) AS count
FROM Employee e
JOIN JobSatisfaction js ON e.satisfaction_id = js.id
JOIN AttritionStatus a ON e.attrition_status_id = a.id
GROUP BY js.value, a.value
ORDER BY js.value, a.value;
"""

pd.read_sql_query(query_q2, conn)

"""3: What’s the average income by job level and attrition status?"""

query_q3 = """
SELECT jl.value AS job_level,
       a.value AS attrition,
       ROUND(AVG(e.monthly_income), 2) AS avg_income
FROM Employee e
JOIN JobLevel jl ON e.job_level_id = jl.id
JOIN AttritionStatus a ON e.attrition_status_id = a.id
GROUP BY jl.value, a.value
ORDER BY jl.value, a.value;
"""

pd.read_sql_query(query_q3, conn)

"""4: Is there any pattern between education level and attrition?"""

query_q4 = """
SELECT ed.value AS education_level,
       a.value AS attrition,
       COUNT(*) AS count
FROM Employee e
JOIN EducationLevel ed ON e.education_level_id = ed.id
JOIN AttritionStatus a ON e.attrition_status_id = a.id
GROUP BY ed.value, a.value
ORDER BY ed.value, a.value;
"""

pd.read_sql_query(query_q4, conn)

"""5: How does work-life balance rating correlate with attrition?"""

query_q5 = """
SELECT wlb.value AS work_life_balance,
       a.value AS attrition,
       COUNT(*) AS count
FROM Employee e
JOIN WorkLifeBalance wlb ON e.wlb_id = wlb.id
JOIN AttritionStatus a ON e.attrition_status_id = a.id
GROUP BY wlb.value, a.value
ORDER BY wlb.value, a.value;
"""

pd.read_sql_query(query_q5, conn)

"""# **PANDAS**

Q1
"""

df_attrition_csv = (
    df_csv.groupby(["Job Role", "Attrition"])
    .size()
    .reset_index(name="count")
    .sort_values(["Job Role", "Attrition"])
)

display(df_attrition_csv)

"""Q2"""

df_satisfaction_csv = (
    df_csv.groupby(["Job Satisfaction", "Attrition"])
    .size()
    .reset_index(name="count")
    .sort_values(["Job Satisfaction", "Attrition"])
)
display(df_satisfaction_csv)

"""Q3"""

df_income_csv = (
    df_csv.groupby(["Job Level", "Attrition"])["Monthly Income"]
    .mean()
    .round(2)
    .reset_index()
    .rename(columns={"Monthly Income": "avg_income"})
    .sort_values(["Job Level", "Attrition"])
)

display(df_income_csv)

"""Q4"""

df_education_csv = (
    df_csv.groupby(["Education Level", "Attrition"])
    .size()
    .reset_index(name="count")
    .sort_values(["Education Level", "Attrition"])
)
display(df_education_csv)

"""Q5"""

df_wlb_csv = (
    df_csv.groupby(["Work-Life Balance", "Attrition"])
    .size()
    .reset_index(name="count")
    .sort_values(["Work-Life Balance", "Attrition"])
)
display(df_wlb_csv)

"""# **VISUALIZATION**

Q1
"""

plt.figure(figsize=(12, 6))
sns.barplot(data=df_attrition_csv, x="Job Role", y="count", hue="Attrition")

plt.title("Attrition Count by Job Role")
plt.xlabel("Job Role")
plt.ylabel("Number of Employees")
plt.xticks(rotation=45)
plt.legend(title="Attrition Status")
plt.tight_layout()
plt.show()

"""Q2"""

left_counts = df_satisfaction_csv[df_satisfaction_csv["Attrition"] == "Left"].set_index("Job Satisfaction")["count"]
stayed_counts = df_satisfaction_csv[df_satisfaction_csv["Attrition"] == "Stayed"].set_index("Job Satisfaction")["count"]
fig, axes = plt.subplots(1, 2, figsize=(14, 7))

axes[0].pie(left_counts, labels=left_counts.index, autopct="%1.1f%%", startangle=90)
axes[0].set_title("Attrition (Left) by Job Satisfaction")
axes[0].axis("equal")  # Equal aspect ratio to ensure it's a circle

axes[1].pie(stayed_counts, labels=stayed_counts.index, autopct="%1.1f%%", startangle=90)
axes[1].set_title("Attrition (Stayed) by Job Satisfaction")
axes[1].axis("equal")

plt.tight_layout()
plt.show()

"""Q3"""

plt.figure(figsize=(10, 6))
sns.barplot(data=df_income_csv, y="Job Level", x="avg_income", hue="Attrition", orient="h", palette="muted") # Try "Set1", "Set2", "Set3", "pastel", "muted"

plt.title("Average Income by Job Level and Attrition (Horizontal)")
plt.xlabel("Average Monthly Income")
plt.ylabel("Job Level")
plt.legend(title="Attrition")
plt.tight_layout()
plt.show()

"""Q4"""

edu_pivot = df_education_csv.pivot(index="Education Level", columns="Attrition", values="count")
edu_pivot.plot(
    kind="bar",
    stacked=True,
    figsize=(10, 6),
    colormap="Set2"
)

plt.title("Stacked Attrition by Education Level")
plt.xlabel("Education Level")
plt.ylabel("Number of Employees")
plt.legend(title="Attrition")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

"""Q5"""

import matplotlib.pyplot as plt

# Combine labels and counts
df_combined = df_wlb_csv.copy()
df_combined["label"] = df_combined["Attrition"] + " - " + df_combined["Work-Life Balance"]

# Data for the pie chart
counts = df_combined["count"]
labels = df_combined["label"]

# Create donut chart
plt.figure(figsize=(8, 8))
plt.pie(
    counts,
    labels=labels,
    autopct="%1.1f%%",
    startangle=90,
    wedgeprops={"width": 0.4}
)

plt.title("Attrition by Work-Life Balance (Donut Chart)")
plt.axis("equal")
plt.tight_layout()
plt.show()

