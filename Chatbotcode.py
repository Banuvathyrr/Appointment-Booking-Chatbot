
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import calendar
import openai
import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta, time

app = Flask(__name__)
from flask import Flask, send_from_directory



@app.route("/")
def home():
    return "Welcome to the CMC Hospital Vellore Appointment Bot. Please use the /whatsapp endpoint to interact with the bot."


# OpenAI API setup
#openai_api_key
#openai.api_key = openai_api_key

# MongoDB Atlas setup
mongo_connection_string = "mongodb+srv://*********@cluster0.vxy7x.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_connection_string)
db = client["doctor_appointments_db"]
appointments_collection = db["appointments"]
users_collection = db["users"]
print("connection success")

# Sample departments and their availability
departments = {
    "cardiology": {"days": ["Mon", "Wed", "Fri"], "start_time": time(10, 0), "end_time": time(14, 0)},
    "neurology": {"days": ["Tue", "Thu"], "start_time": time(12, 0), "end_time": time(15, 0)},
    "pediatrics": {"days": ["Mon", "Wed", "Fri"], "start_time": time(9, 0), "end_time": time(13, 0)},
    "gynecology": {"days": ["Tue", "Thu"], "start_time": time(13, 0), "end_time": time(16, 0)},
    "dermatology": {"days": ["Mon", "Thu"], "start_time": time(11, 0), "end_time": time(15, 0)},
    "orthopedics": {"days": ["Tue", "Fri"], "start_time": time(10, 0), "end_time": time(14, 0)}
}

department_mapping = {
    "1": "cardiology",
    "1.cardiology": "cardiology",
    "2": "neurology",
    "2.neurology": "neurology",
    "3": "pediatrics",
    "3.pediatrics": "pediatrics",
    "4": "gynecology",
    "4.gynecology": "gynecology",
    "5": "dermatology",
    "5.dermatology": "dermatology",
    "6": "orthopedics",
    "6.orthopedics": "orthopedics"
}

# In-memory user state storage
user_states = {} #global dictionary that holds the state and data for each useR

def update_user_state(from_number, state, data=None):
    """Update the user's current state and data."""
    user_states[from_number] = {"state": state, "data": data or {}}

def get_user_state(from_number):
    """Retrieve the user's current state and data."""
    return user_states.get(from_number, {"state": "start", "data": {}})

def generate_answer(question):
    """Generate answers using ChatGPT"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question},
            ],
            temperature=0.5,
            max_tokens=150,
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print(f"Error generating answer: {e}")
        return "I'm sorry, I couldn't process that. Please try again."

def validate_date_time(date_time_str):
    """Validate time in format 'HH:MM AM/PM'."""
    try:
        datetime.strptime(date_time_str, '%I:%M %p')
        return True
    except ValueError:
        return False


def check_availability(department, requested_datetime):
    # Get the department's availability information
    dept_info = departments.get(department.lower())
    if not dept_info:
        return False  # If the department doesn't exist, return False
    
    # Extract requested day and time
    requested_day = requested_datetime.strftime("%a")  # Get the day in short form, e.g., "Mon", "Tue"
    #requested_time = requested_datetime.time()  # Extract the time part of the datetime
    
    if requested_day in dept_info["days"]:
        return True  # Slot is available
    
    return False 



def check_available_time(department, requested_datetime):
    # Get the department's availability information
    dept_info = departments.get(department.lower())
    if not dept_info:
        return False  # If the department doesn't exist, return False
            
    requested_time = requested_datetime.time()  # Extract the time part of the datetime

    if dept_info["start_time"] <= requested_time <= dept_info["end_time"]:
        # Check MongoDB for existing appointments in the same department at the same time
        existing_appointment = appointments_collection.find_one({
            "department": department.lower(),
            "appointment_datetime": requested_datetime
        })
        if existing_appointment:
            return False  # Slot is already booked
        return True # Slot is available
    return False

       

def validate_date_range(year, month, day):
    """Validate if the day exists in the given month and year."""
    try:
        date_obj = datetime(year, month, day)
        return True
    except ValueError:
        return False


def book_appointment(patient_name, department, appointment_datetime, mobile_number):
    """Store the appointment in MongoDB."""
    appointment_data = {
        "patient_name": patient_name,
        "department": department,
        "appointment_datetime": appointment_datetime.strftime('%Y-%m-%d %I:%M %p'),
        "mobile_number": mobile_number
    }
    appointments_collection.insert_one(appointment_data)
    return f"Appointment confirmed for {patient_name} in {department} on {appointment_datetime.strftime('%Y-%m-%d %I:%M %p')}. Confirmation sent to {mobile_number}."



def generate_calendar(year, month):
    """Generate a text representation of a calendar for the given month and year."""
    cal = calendar.TextCalendar(calendar.SUNDAY)
    return cal.formatmonth(year, month)



@app.route("/whatsapp", methods=['POST'])
def wa_reply():
    from_number = request.form.get('From') # extract from_no from the incoming post request payload (ie twilio whatsapp API)
    query = request.form.get('Body').strip() # extract message body from incoming post request payload (ie twilio whatsapp API)
    print(f"User ({from_number}) Query: {query}")
    
    twilio_response = MessagingResponse()
    reply = twilio_response.message()
    
    user = get_user_state(from_number) # Calls the get_user_state function with from_number to retrieve the user's state and data. This function likely returns a dictionary containing keys like "state" and "data"
    current_state = user.get("state", "start") # Uses the dictionary get() method on user to retrieve the "state" value. If the "state" key isn’t found, it defaults to "start". 
    user_data = user.get("data", {})

    if current_state == "start":
        if "book appointment" in query.lower():
            # Skip the welcome message and proceed directly to booking
            reply.body("Sure, let's book an appointment. Please provide your Full Name:")
            update_user_state(from_number, "awaiting_name", user_data)
        else:
            # Send welcome message for the first interaction
            reply.body("Welcome to CMC Hospital Vellore!\nTo book an appointment, type 'book appointment'.")
    
        
    
    elif current_state == "awaiting_name":
        user_data['patient_name'] = query.title()
        reply.body("Great, please select the department you want to book an appointment for:\n"
               "1. Cardiology\n"
               "2. Neurology\n"
               "3. Pediatrics\n"
               "4. Gynecology\n"
               "5. Dermatology\n"
               "6. Orthopedics")
        update_user_state(from_number, "awaiting_department", user_data)
        #update_user_state(from_number, "awaiting_department", user_data)
    
    
    elif current_state == "awaiting_department":
        dept_input = query.lower().strip()
        dept = department_mapping.get(dept_input, None)  # Get the mapped department name
        if dept in departments:
            user_data['department'] = dept
            # Format the availability information
            days_available = ", ".join(departments[dept]['days'])
            start_time = departments[dept]['start_time'].strftime("%I:%M %p")
            end_time = departments[dept]['end_time'].strftime("%I:%M %p")
            reply.body(f"Doctor availability for {dept.capitalize()}:\n"
                    f"Days - {days_available}\n"
                    f"Time - {start_time} to {end_time}\n\n"
                    f"Please enter the appointment date (format: YYYY-MM-DD):")
            update_user_state(from_number, "awaiting_date", user_data)
        else:
            reply.body("Invalid selection. Please try again with a valid department number or name.")
            
    
    elif current_state == "awaiting_date":
        try:
            if len(query.split('-')) != 3:
                raise ValueError("Invalid date format. Please enter a valid date (format: YYYY-MM-DD).")

            # Parse the input as YYYY-MM-DD
            year, month, day = map(int, query.split('-'))
            current_date = datetime.now()

            # Validate the month and year
            if year < current_date.year or (year == current_date.year and month < current_date.month):
                raise ValueError("Past month and year not allowed.")

            if not (1 <= month <= 12):
                raise ValueError("Invalid month.")

            # Validate the day for the given month and year
            if not validate_date_range(year, month, day):
                raise ValueError("Invalid date for the month.")

            # Ensure the selected date is not in the past
            selected_date = datetime(year, month, day)
            if selected_date < current_date:
                raise ValueError("Past dates not allowed.")

            # Check availability
            if check_availability(user_data['department'], selected_date):
                user_data['appointment_date'] = f"{year}-{month:02d}-{day:02d}"
                reply.body("Please enter your preferred appointment time (format: HH:MM AM/PM):")
                update_user_state(from_number, "awaiting_time", user_data)
            else:
                reply.body("The selected date is unavailable for this department. Please choose another date.")

        except ValueError as e:
        # Handle specific validation messages
            reply.body(str(e) if str(e) else "Invalid date format. Please enter a valid date (format: YYYY-MM-DD).")



    elif current_state == "awaiting_time":
        if validate_date_time(query):
            user_data['appointment_time'] = query
            #reply.body(f"Please confirm your appointment:\nName: {user_data['patient_name']}\nDepartment: {user_data['department'].capitalize()}\nDate: {user_data['appointment_date']}\nTime: {user_data['appointment_time']}\nMobile: {user_data.get('patient_mobile_number', from_number)}\nReply with 'confirm' to book or 'cancel' to abort.")
            requested_datetime_str = f"{user_data['appointment_date']} {user_data['appointment_time']}"
            requested_datetime = datetime.strptime(requested_datetime_str, '%Y-%m-%d %I:%M %p')
            
            
            if check_available_time(user_data['department'], requested_datetime):
                
                confirmation_message = book_appointment(
                    user_data['patient_name'], user_data['department'], 
                    requested_datetime, from_number
                )
                reply.body(f"Please confirm your appointment:\nName: {user_data['patient_name']}\nDepartment: {user_data['department'].capitalize()}\nDate: {user_data['appointment_date']}\nTime: {user_data['appointment_time']}\nMobile: {user_data.get('patient_mobile_number', from_number)}\nReply with 'confirm' to book or 'cancel' to abort.\nOr reply with 'yes' if you want to talk with a staff member.")
                update_user_state(from_number, "awaiting_confirmation", user_data)
                #reply.body(confirmation_message)
                #update_user_state(from_number, "start")
            else:
                
                reply.body("The requested slot is unavailable. Please try a different time.")
                update_user_state(from_number, "awaiting_time", user_data)
                #reply.body(f"Please confirm your appointment:\nName: {user_data['patient_name']}\nDepartment: {user_data['department'].capitalize()}\nDate: {user_data['appointment_date']}\nTime: {user_data['appointment_time']}\nMobile: {user_data.get('patient_mobile_number', from_number)}\nReply with 'confirm' to book or 'cancel' to abort.")
                #update_user_state(from_number, "awaiting_confirmation", user_data)
                
        else:
            reply.body("Invalid time format. Please enter the time in HH:MM AM/PM format.")
            reply.body(f"Please confirm your appointment:\nName: {user_data['patient_name']}\nDepartment: {user_data['department'].capitalize()}\nDate: {user_data['appointment_date']}\nTime: {user_data['appointment_time']}\nMobile: {user_data.get('patient_mobile_number', from_number)}\nReply with 'confirm' to book or 'cancel' to abort.")
            update_user_state(from_number, "awaiting_confirmation", user_data)

    elif current_state == "awaiting_confirmation":
        if query.lower() == "confirm":
            
            #confirmation_message = book_appointment(
            #    user_data['patient_name'], user_data['department'], 
            #    f"{user_data['appointment_date']} {user_data['appointment_time']}", 
            #    from_number
            #)
            #reply.body(confirmation_message)
            #reply.body("Would you like to book another appointment or exit the chat?\nReply with 'book again' or 'exit'.")
            reply.body(
                    f"Your appointment has been successfully booked.\n"
                    f"Details:\n"
                    f"Name: {user_data['patient_name']}\n"
                    f"Department: {user_data['department'].title()}\n"
                    f"Date: {user_data['appointment_date']}\n"
                    f"Time: {user_data['appointment_time']}\n\n"
                    #f"Mobile: {user_data.get('patient_mobile_number', from_number)}\n\n"
                    "Please arrive at least 10 minutes before your scheduled time.\n"
                    "Would you like to book another appointment or exit the chat?\n"
                    "Reply with **Book Again** or **Exit**."
                )
            update_user_state(from_number, "post_confirmation", user_data)
            
        elif query.lower() == "cancel":
            reply.body("Appointment booking cancelled. To start again, type 'book appointment'.")
            update_user_state(from_number, "post_confirmation", {})
            #update_user_state(from_number, "start")

        elif query.lower() == "yes":
            # If user wants to talk to staff
            reply.body("Please hold on. A staff member will assist you shortly.")
            update_user_state(from_number, "start")  # Reset state for staff communication

        else:
            reply.body("Invalid response. Please reply with 'confirm' to book, 'cancel' to abort, or 'yes' to talk with a staff member.")
            update_user_state(from_number, "awaiting_confirmation", user_data)

    elif current_state == "post_confirmation":
        if "book again" in query.lower():
            reply.body("Sure, let's start over. Please provide your Full Name:")
            update_user_state(from_number, "awaiting_name")
        elif "exit" in query.lower():
            reply.body("Thank you for using CMC Hospital Vellore Appointment Bot. Have a great day!")
            update_user_state(from_number, "start", {})
        else:
            reply.body("Please reply with 'book again' to book another appointment or 'exit' to end the chat.")
    else:
        reply.body("Sorry, I didn't understand that. Can you please rephrase?")
    
    return str(twilio_response)

if __name__ == "__main__":
    app.run(debug=True)
