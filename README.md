# VulnerableApp - Learn & Hack!

Welcome to **VulnerableApp**, a purposefully insecure web application designed for security professionals and ethical hackers to practice real-world attacks.

This app comes with a **Lab Guide (Vulnerable App Lab Guide.pdf)** that walks you through various vulnerabilities, including:

- 🔑 **Authentication Bypass**
- 🛡 **Creating High-Privilege Accounts**
- ⚡ **Cross-Site Scripting (XSS)**
- 🎭 **Session Hijacking**
- 🔍 **SQL Injection**
- 🔎 **Hidden Pages & Sensitive Data Exposure**
- 💻 **Command Injection**
- 📂 **Local File Inclusion (LFI)**
- 🔗 **Insecure Direct Object References (IDOR)**

---

##  Getting Started

### **1. Run the Application**

To get started, navigate to the directory where **Vulnerable App** is located and run:

```bash
python3 app.py
```
---

##  Changing the Default Port

To get started, navigate to the directory where **Vulnerable App** is located edit app.py.  You will need to change the last line of the file which will look like:

```bash
app.run(host='0.0.0.0', port=80, debug=True)
```

Simply replace 80 with your desired port

## 📜 Lab Guide

The **Lab Guide (Vulnerable App Lab Guide.pdf)** provides hands-on exercises and challenges to help you exploit the vulnerabilities in this application.

🔍 **Your mission:** Explore, break, and learn! 🕵️‍♂️

---

## ⚠️ Disclaimer

This application is for **educational purposes only**. Do **not** deploy it on a public-facing server or use it for malicious activities.
