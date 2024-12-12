<h1 align="center"> DOCTOR APPOINTMENT BOOKING CHATBOT </h1>  


**PROJECT OVERVIEW**
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
This project is a Doctor Appointment Booking Chatbot developed using Flask, Twilio's WhatsApp API, OpenAI's GPT-3.5, and MongoDB. It allows users to schedule appointments with various hospital departments via WhatsApp, providing a seamless and interactive experience. The chatbot handles user interactions, validates inputs, checks availability, and books appointments efficiently.

<p align="center">
  <img src="https://github.com/user-attachments/assets/c3f0d056-0e24-4e3e-94de-8847ad3c891e" width="400" height="800">
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/87aa5ec0-5d4c-47b4-b38c-5989f8099dc3" width="400" height="800">
</p>



 
**KEY FEATURES** 
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**User Interaction via WhatsApp:**
- Patients can interact with the chatbot to book appointments using natural language queries.
- The chatbot guides users step-by-step through the booking process.
  
**Department Availability Management:**  
- Each department has predefined availability days and time slots.  
- Appointment scheduling ensures no overlapping of bookings for the same slot.
  
**Dynamic Responses with OpenAI GPT:**  
- The chatbot can answer general queries with GPT-generated responses.
  
**Database Integration with MongoDB:**  
- Stores appointment details and user information.  
- Validates and checks availability in real time to ensure accurate booking.
  
**Appointment Validation:**  
- Ensures that requested dates and times match the department’s working hours.  
- Provides real-time feedback on available or unavailable slots.
  
**Calendar Display:**  
- Offers a text-based calendar for user reference when selecting dates.


   
**TECH STACK**
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**Backend Framework:** Flask  
**Messaging API:** Twilio WhatsApp API  
**AI Integration:** OpenAI GPT-3.5 for conversational responses  
**Database:** MongoDB (MongoDB Atlas for cloud storage)  
**Programming Language:** Python  
**Deployment:** Flask server      



**WORKFLOW**  
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**1.Welcome Message:**
- The chatbot starts by introducing itself and guiding users to type "book appointment" to initiate the process.
  
**User Information Collection:**  
- Collects the patient's name, preferred department, date, and time slot.
  
**Availability Check:**
- Matches the requested date and time with the department's schedule.  
- Checks MongoDB for conflicts to prevent double booking.
  
**Appointment Confirmation:**
- Confirms the booking and sends a confirmation message with details such as department, date, time, and patient name.  

**Error Handling:**
- Handles invalid inputs with clear error messages and retries.



**Department Details**
Each department has predefined working days and time slots:  
Cardiology: Mon, Wed, Fri (10:00 AM - 2:00 PM)  
Neurology: Tue, Thu (12:00 PM - 3:00 PM)  
Pediatrics: Mon, Wed, Fri (9:00 AM - 1:00 PM)  
Gynecology: Tue, Thu (1:00 PM - 4:00 PM)  
Dermatology: Mon, Thu (11:00 AM - 3:00 PM)  
Orthopedics: Tue, Fri (10:00 AM - 2:00 PM)  



**MongoDB Schema**  
**Appointments Collection:**
- patient_name: Name of the patient
- department: Department name
- appointment_datetime: Scheduled date and time
- mobile_number: User's phone number
       
**Users Collection:**  
- Stores user details for enhanced personalization (future scope).  



**FUTURE ENHANCEMENTS**  
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
- Add multilingual support.  
- Enable rescheduling and canceling appointments.  
- Integrate payment options for paid consultations.  
- Enhance AI responses with contextual patient history.
 
**DEMO LINK**
https://drive.google.com/drive/folders/1DVrap-SjWwkBiljb5nA3il60UO_DPfBp?usp=sharing
