# Grievance Tracker

An intelligent grievance management system built using **Streamlit** and **Python**. This project allows users to submit grievances, automatically categorizes them, scores their urgency, and enables administrators to manage and escalate issues efficiently.

---

## Features

- Grievance Submission  
  Users can submit detailed grievances with descriptions and supporting documents (optional).

- Automatic Categorization  
  Categorizes complaints into areas such as Water Supply, Road Damage, Electricity, and Garbage using keyword detection.

- Priority Scoring System  
  Calculates urgency based on the content of the grievance using a rule-based keyword model.

- Auto Escalation  
  Issues pending for more than 3 days are automatically escalated and marked as such.

- Admin Dashboard  
  Filter, review, and update the status of submitted grievances with suggested follow-up actions.

- Track Grievance History  
  Users can view all their previous complaints and status history using their name.

- Feedback and Reopening  
  Allows users to reopen unresolved complaints or give feedback after resolution.

---

## Tech Stack

- Python
- Streamlit
- Pandas
- JSON (for local grievance storage)

---

## Project Structure

grievance-tracker/
├── app.py # Main application logic
├── grievances.json # JSON database for storing grievances
├── uploads/ # Uploaded documents (optional)


---

## Getting Started

1. Install Dependencies

```bash
pip install streamlit pandas
