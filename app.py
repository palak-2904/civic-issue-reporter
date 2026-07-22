import streamlit as st
import pandas as pd
import os
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from database import init_db, add_report, get_all_reports, get_reports_by_user, update_status

# Database initialize karo
init_db()

# Uploads folder banao agar nahi hai
os.makedirs("uploads", exist_ok=True)

st.set_page_config(page_title="Civic Issue Reporter", layout="wide")
st.title("Neighborhood Issue Reporter")

# ---------- AI Model Load Karo (sirf ek baar, cache karke) ----------
@st.cache_resource
def load_classifier():
    model = load_model("civic_classifier.h5")
    with open("class_names.txt", "r") as f:
        class_names = [line.strip() for line in f.readlines()]
    return model, class_names

model, class_names = load_classifier()

def predict_category(image_path):
    """Photo se category predict karta hai"""
    img = Image.open(image_path).convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    predictions = model.predict(img_array, verbose=0)
    predicted_index = np.argmax(predictions[0])
    confidence = predictions[0][predicted_index] * 100
    predicted_class = class_names[predicted_index]

    return predicted_class, confidence

# Sidebar navigation
menu = st.sidebar.selectbox("Menu", ["Report an issue", "My reports", "Admin dashboard"])

# ---------- PAGE 1: Report an issue ----------
if menu == "Report an issue":
    st.header("Report a new issue")

    name = st.text_input("Your name / flat number")
    photo = st.file_uploader("Upload a photo", type=["jpg", "jpeg", "png"])

    predicted_category = None

    # ---------- Photo upload hote hi AI prediction ----------
    if photo is not None:
        temp_path = f"uploads/temp_{photo.name}"
        with open(temp_path, "wb") as f:
            f.write(photo.getbuffer())

        st.image(temp_path, width=250, caption="Uploaded photo")

        predicted_category, confidence = predict_category(temp_path)
        st.info(f"AI detected: **{predicted_category.capitalize()}** ({confidence:.1f}% confidence)")

    # User AI prediction confirm ya change kar sakta hai
    all_categories = ["Pothole", "Garbage", "Streetlight", "Water leakage", "Other"]
    default_index = 0
    if predicted_category:
        matched = [c for c in all_categories if c.lower() == predicted_category.lower()]
        if matched:
            default_index = all_categories.index(matched[0])

    category = st.selectbox("Confirm or change category", all_categories, index=default_index)
    description = st.text_area("Describe the issue")
    location = st.text_input("Location (e.g. Block A, near gate 2)")

    if st.button("Submit report"):
        if name and description and location:
            image_path = ""
            if photo is not None:
                image_path = f"uploads/{photo.name}"
                with open(image_path, "wb") as f:
                    f.write(photo.getbuffer())

            add_report(category, description, location, image_path, name)
            st.success("Report submitted")
        else:
            st.error("Please fill name, description and location")

# ---------- PAGE 2: My reports ----------
elif menu == "My reports":
    st.header("Track your reports")
    name = st.text_input("Enter your name / flat number to view your reports")

    if name:
        reports = get_reports_by_user(name)
        if reports:
            for r in reports:
                with st.container(border=True):
                    st.write(f"**{r[1]}** — {r[3]}")
                    st.write(r[2])
                    st.write(f"Status: **{r[5]}**")
                    st.caption(f"Reported on {r[7]}")
        else:
            st.info("No reports found for this name")

# ---------- PAGE 3: Admin dashboard ----------
elif menu == "Admin dashboard":
    st.header("Admin dashboard")

    reports = get_all_reports()
    if reports:
        df = pd.DataFrame(reports, columns=[
            "ID", "Category", "Description", "Location",
            "Image", "Status", "Reported By", "Created At"
        ])

        col1, col2, col3 = st.columns(3)
        col1.metric("Total reports", len(df))
        col2.metric("Pending", len(df[df["Status"] == "Pending"]))
        col3.metric("Resolved", len(df[df["Status"] == "Resolved"]))

        st.subheader("Issues by category")
        st.bar_chart(df["Category"].value_counts())

        st.subheader("All reports")
        for r in reports:
            with st.container(border=True):
                st.write(f"**#{r[0]} — {r[1]}** ({r[3]})")
                st.write(r[2])
                new_status = st.selectbox(
                    "Status", ["Pending", "In Progress", "Resolved"],
                    index=["Pending", "In Progress", "Resolved"].index(r[5]),
                    key=f"status_{r[0]}"
                )
                if new_status != r[5]:
                    update_status(r[0], new_status)
                    st.rerun()
    else:
        st.info("No reports yet")