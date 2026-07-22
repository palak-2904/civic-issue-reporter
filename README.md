# Neighborhood Issue Reporter

AI-powered civic issue reporting platform that lets residents report problems 
like potholes and garbage collection issues with automatic image classification.

## Features
- Report issues with photo, location, and description
- AI-based image classification (CNN, transfer learning on MobileNetV2)
- Real-time status tracking (Pending / In Progress / Resolved)
- Admin dashboard with analytics

## Tech Stack
Python, Streamlit, TensorFlow/Keras, SQLite, Pandas

## How it works
1. User uploads a photo of the issue
2. A CNN model (trained via transfer learning) predicts the category
3. User confirms/edits the category and submits
4. Admin can track and update status via dashboard

## Live Demo
https://civic-issue-reporter-m0mq.onrender.com
