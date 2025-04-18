import streamlit as st
import json
import os
import datetime
import pandas as pd
import uuid

# Load / Save Helpers
def load_grievances():
    if os.path.exists("grievances.json"):
        with open("grievances.json", "r") as f:
            return json.load(f)
    return []

def save_grievances(grievances):
    with open("grievances.json", "w") as f:
        json.dump(grievances, f, indent=4)

# Logic Functions for Categorization and Priority
def extract_keywords(text):
    return [word for word in text.lower().split() if len(word) > 4]

def categorize_grievance(text):
    categories = {
        "Water Supply": ["water", "supply", "tap"],
        "Garbage": ["garbage", "trash", "waste"],
        "Electricity": ["electric", "light", "power"],
        "Road Damage": ["road", "pothole", "crack"]
    }
    for category, keywords in categories.items():
        if any(keyword in text.lower() for keyword in keywords):
            return category
    return "Other"

def grievance_score(text):
    score = 0

    # High Urgency Keywords (Critical Issues)
    urgent_keywords = ["urgent", "danger", "injury", "critical", "emergency", "life-threatening", "fire", "flood", "accident", "immediate", "disaster"]
    
    # Medium Urgency Keywords (Important Issues)
    medium_keywords = ["important", "delayed", "issue", "complaint", "damaged", "repair", "malfunction", "urgent", "critical", "problem"]
    
    # Low Urgency Keywords (Non-Emergency Issues)
    low_keywords = ["routine", "normal", "minor", "checkup", "maintenance", "scheduled", "repair", "recheck", "regular", "ongoing"]
    
    # High Urgency Scoring
    for word in urgent_keywords:
        if word in text.lower():
            score += 40  # Higher points for critical keywords
    
    # Medium Urgency Scoring
    for word in medium_keywords:
        if word in text.lower():
            score += 20  # Moderate points for medium urgency keywords
    
    # Low Urgency Scoring
    for word in low_keywords:
        if word in text.lower():
            score += 5  # Low points for non-urgent keywords

    # Penalize unresolved grievances
    if "not resolved" in text.lower() or "again" in text.lower():
        score += 25

    # Ensure that the score doesn't exceed 100 (highest priority)
    return min(score + 50, 100)  # Add base score to the final score

def suggest_action(category, priority):
    # Assign next level action based on priority
    actions = {
        "Water Supply": "Forward to Jal Nigam for urgent inspection" if priority > 70 else "Forward to Jal Nigam for regular check",
        "Road Damage": "Notify PWD for immediate repair" if priority > 70 else "Notify PWD for standard check",
        "Garbage": "Alert sanitation department for immediate cleaning" if priority > 70 else "Alert sanitation department for routine collection",
        "Electricity": "Notify electricity board for urgent check" if priority > 70 else "Notify electricity board for regular maintenance"
    }
    return actions.get(category, "Review and assign appropriate department.")

def auto_escalate(grievance):
    # Automatically escalate if unresolved and more than 3 days old
    today = datetime.date.today()
    g_date = datetime.datetime.strptime(grievance['Date'], "%Y-%m-%d").date()
    if grievance['Status'] == "Pending" and (today - g_date).days > 3:
        grievance['Escalated'] = "Yes"
        grievance['Status'] = "Escalated"
        return True
    return False

# App Setup
st.set_page_config("Jan Darpan - Grievance Tracker", layout="wide")
st.title("Jan Darpan - AI-Powered Grievance Tracker")

menu = ["Submit Grievance", "Admin Panel", "Track History", "Feedback & Reopen"]
choice = st.sidebar.radio("Navigate", menu)

grievances = load_grievances()
upload_dir = "uploads"
os.makedirs(upload_dir, exist_ok=True)

# Submit Grievance
if choice == "Submit Grievance":
    with st.form("grievance_form"):
        st.subheader(" Submit New Grievance")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Your Name")
        with col2:
            grievance_date = st.date_input("Date", value=datetime.date.today())

        grievance_text = st.text_area("Describe your grievance")
        uploaded_image = st.file_uploader("📷 Upload Image (Optional)", type=["jpg", "jpeg", "png"])
        uploaded_doc = st.file_uploader("📄 Upload Document (Optional)", type=["pdf", "docx"])

        submitted = st.form_submit_button("Submit Grievance")

    if submitted:
        if name and grievance_text:
            grievance_id = str(uuid.uuid4())[:8]
            category = categorize_grievance(grievance_text)
            priority = grievance_score(grievance_text)
            keywords = extract_keywords(grievance_text)
            image_path = None
            doc_path = None
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

            if uploaded_image:
                image_path = os.path.join(upload_dir, f"{name}_{timestamp}_image.png")
                with open(image_path, "wb") as f:
                    f.write(uploaded_image.read())

            if uploaded_doc:
                ext = uploaded_doc.name.split('.')[-1]
                doc_path = os.path.join(upload_dir, f"{name}_{timestamp}_doc.{ext}")
                with open(doc_path, "wb") as f:
                    f.write(uploaded_doc.read())

            grievances.append({
                "ID": grievance_id,
                "Name": name,
                "Text": grievance_text,
                "Category": category,
                "Date": str(grievance_date),
                "Priority": priority,
                "Keywords": keywords,
                "Status": "Pending",
                "Escalated": "No",
                "Image": image_path,
                "Attachment": doc_path
            })
            save_grievances(grievances)
            st.success(f"✅ Grievance Submitted! Your Reference ID: {grievance_id}")
        else:
            st.warning("Please fill in all fields.")

# Admin Panel
elif choice == "Admin Panel":
    st.subheader("Admin Dashboard")

    if grievances:
        df = pd.DataFrame(grievances)
        df['Suggested Action'] = df['Category'].apply(lambda x: suggest_action(x, df.loc[df['Category'] == x, 'Priority'].max()))

        # Filters
        status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Resolved", "Escalated"])
        if status_filter != "All":
            df = df[df["Status"] == status_filter]

        cat_filter = st.multiselect("Filter by Category", df["Category"].unique())
        if cat_filter:
            df = df[df["Category"].isin(cat_filter)]

        st.dataframe(df.sort_values(by="Priority", ascending=False), use_container_width=True)

        # Update Status
        st.markdown("---")
        st.subheader("📝 Update Grievance Status")
        selected_id = st.selectbox("Select Grievance ID", [g['ID'] for g in grievances])
        new_status = st.selectbox("Update Status To", ["Pending", "Resolved", "Escalated"])

        if st.button("✅ Update Status"):
            for g in grievances:
                if g["ID"] == selected_id:
                    g["Status"] = new_status
                    auto_escalate(g)  # Auto escalate unresolved grievances
            save_grievances(grievances)
            st.success(f"Status updated to {new_status} for ID {selected_id}")

    else:
        st.info("No grievances available yet.")

# Track History
elif choice == "Track History":
    st.subheader("Track Your Grievance")
    name = st.text_input("Enter your name to search")
    if name:
        records = [g for g in grievances if g["Name"].lower() == name.lower()]
        if records:
            st.write(pd.DataFrame(records))
        else:
            st.warning("No records found.")

# Feedback
elif choice == "Feedback & Reopen":
    st.subheader("Feedback or Reopen Case")
    name = st.text_input("Your Name")
    feedback = st.text_area("Enter your feedback or reason to reopen")

    if st.button("📩 Submit Feedback"):
        if name and feedback:
            st.success("✅ Feedback noted. Concern will be reviewed again.")
        else:
            st.warning("Please fill in all fields.")
