from flask import Flask, render_template, request
import plotly
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
import json

app = Flask(__name__)

# MongoDB connection
connection_string = "mongodb+srv://banuser:Thanabanu%401@cluster0.vxy7x.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(connection_string)
db = client["doctor_appointments_db"]
collection = db["appointments"]

# Fetch data from MongoDB
def get_appointments(department):
    query = {"department": department}
    appointments = list(collection.find(query))
    df = pd.DataFrame(appointments)
    if "_id" in df.columns:
        df = df.drop("_id", axis=1)
    return df

# Flask routes
@app.route("/test") # to verify database connectivity and schema.
def test_connection():
    try:
        departments = collection.distinct("department") #Queries the MongoDB collection to get unique values from the department field.
        return f"Departments: {departments}"
    except Exception as e:
        return f"Error: {e}"


@app.route("/") # Home page
def index(): # Provides the starting interface where users can select a department.
    # Show dropdown for department selection
    departments = collection.distinct("department")  # Fetch unique departments
    print(departments)
    return render_template("dashboard.html", departments=departments)

@app.route("/dashboard", methods=["POST"]) #POST is used here because the route processes form data submitted by the user.
def dashboard():
    # Get selected department
    department = request.form.get("department") #Retrieves the selected department value from the form submitted by the user on the homepage (index route).
    data = get_appointments(department) #The app fetches relevant data from MongoDB using get_appointments
    departments = collection.distinct("department")

    if not data.empty:
        # Use the correct column 'appointment_datetime' instead of 'Date'
        data['appointment_datetime'] = pd.to_datetime(data['appointment_datetime'])
        #count_by_date = data.groupby(data['appointment_datetime'].dt.date).size().reset_index(name='Count')
        #fig = px.bar(count_by_date, x='appointment_datetime', y='Count', title=f"Appointments for {department}")
        #graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder) #Converts the chart object into JSON format for rendering in the HTML template.

        # Render template with data and chart
        return render_template(
            "dashboard.html",
            departments=departments, #  List of all department names (for the dropdown).
            data=data.to_dict(orient="records"), # Raw appointment data converted to dictionary format.
            #graphJSON=graphJSON, #JSON representation of the bar chart (thats how the the frontend (HTML/JavaScript) interacts with the backend (Python))
            selected_department=department, #The department the user selected.
        )

    else:
        # If no data found
        return render_template(
            "dashboard.html",
            departments=departments,
            error=f"No appointments found for {department}.",
        )

if __name__ == "__main__":
    app.run(debug=True)
