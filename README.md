# 🌊 A-Wave: Security Operations Center Platform

A lightweight, highly optimized Mini-SIEM (Security Information and Event Management) platform built to simulate enterprise SOC operations, log analysis, and AI-driven threat detection.

## 🚀 Key Features
* **Live Telemetry Engine:** Real-time ingestion and normalization of Apache and Syslog data.
* **Optimized WAF:** Regex-compiled detection engine for instantaneous identification of known payloads (SQLi, Brute Force).
* **AI Anomaly Detection:** Scikit-Learn `IsolationForest` model trained on baseline traffic to detect zero-day behavioral deviations.
* **OSINT AI Copilot:** Live internet integration fetching geographic and ISP threat intelligence.
* **Enterprise Architecture:** Hashed credentials (bcrypt), environment secrets (`.env`), and fully Dockerized deployment.

## 🛠️ Tech Stack
* **Backend:** Python 3.10, Flask
* **Database:** SQLite (Centralized Manager for Postgres migration)
* **Machine Learning:** Pandas, Scikit-Learn
* **DevOps:** Docker
* **Frontend:** HTML5, CSS3, Vanilla JS, Chart.js, Leaflet.js

## 📦 Quick Start (Docker)

1. Clone the repository.
2. Create a `.env` file in the root directory:
   ```env
   SECRET_KEY="your_secure_random_string"