<!-- markdownlint-disable MD033 MD013 MD041-->
<div align="center">
<img width="350" height="350" alt="SPM"
     src="https://github.com/user-attachments/assets/162268b3-c81b-4454-bc3a-dbf4a801c475" />
</div>
<!-- markdownlint-enable MD033 MD013 MD041-->

<!-- markdownlint-disable MD033 MD013-->
<div align="center">

# Smart Pantry Manager
<!-- markdownlint-disable MD001-->
### *making your kitchen smarter, one ingredient at a time.*
<!-- markdownlint-enable MD001-->
</div>

Welcome to **Smart Pantry Manager** – a simple and smart web app that helps you
**track what’s in your kitchen**, **avoid food waste**, and **find recipes** using
what you already have.

This project was created as part of the **MIT Emerging Talent Program**

🔗 **Try it here:**
👉 [Smart Pantry Manager – Web App](https://mit-emerging-talent-elo2-smart-pantr-the-appsmart-pantry-iyqurj.streamlit.app/)

---

## 💡 What Does the App Do?

Have you ever opened your fridge and realized something expired last week?
Or wanted to cook, but didn’t know what you could make with what’s left?

**Smart Pantry Manager** helps with that by:

* Letting you **add and track items** in your pantry 🧺
* Showing **expiry alerts** for soon-to-expire products 🕒
* Recommending **recipes** based on your available ingredients 🥗

---

## 🧩 Project Development Stages

### **Stage 1: Foundation – Adding Products & Expiry Alerts**

**Goal:** Build the core of the app.
**What we did:**

* Created an easy interface to add products (name + expiry date).
* Saved items in a CSV file.
* Calculated how many days are left before expiry.
* Displayed alerts for items that are about to expire.

🎯 **Result:** A working base app that tracks expiry dates and sends alerts.

---

### **Stage 2: Smart Suggestions – Recipe Recommendations** ✅ *(Current Stage)*

**Goal:** Help users make use of what they already have.
**What we’re working on now:**

* Adding a recipe database.
* Matching ingredients in the pantry with available recipes.
* Displaying suggested recipes in a clean, friendly interface.

🎯 **Result (in progress):** The app suggests recipes that match ingredients in the
pantry, helping reduce food waste and encourage home cooking.

---

### **Stage 3: Custom Ingredient Selection**

**Goal:** Give users more control over what to cook.
**Plan:**

* Let users manually select ingredients they want to use.
* Show matching recipes dynamically.
* Improve recipe layout for better user experience.

🎯 **Future Result:** More personalized recipe suggestions and interaction.

---

### **Stage 4: Healthy Eating Mode**

**Goal:** Promote mindful and healthy food choices.
**Plan:**

* Add a “Healthy Recipes Only” filter.
* Tag recipes by calorie level or nutrition type.
* Display helpful info like “Low Fat” or “High Protein.”

🎯 **Future Result:** Encourage users to make healthier cooking choices.

---

### **Stage 5: Smart Camera & AI Features** *(Future Plan)*

**Goal:** Make the app more intelligent and user-friendly.
**Plan:**

* Allow users to take photos of food items instead of typing.
* Use AI to automatically detect product names and expiry dates.
* Save product images with their data for easier tracking.
* Analyze user behavior and send smart reminders.
* Sync user data to the cloud for access on multiple devices.

🎯 **Future Result:** A complete AI-powered kitchen assistant that saves time,
reduces waste, and learns from user habits.

---

## 🔧 Tools & Technologies

| Tool                            | Purpose                                     |
| ------------------------------- | --------------------------------------------|
| **Python**                      | Main programming language                   |
| **Streamlit**                   | Web app interface                           |
| **Pandas**                      | Data management and processing              |
| **CSV files**                   | Local storage for items and recipes         |
| **OpenAI / Vision AI (future)** | Planned for automatic detection and AI analysis|

---

## 🚀 How to Run Locally

1. **Clone the repository**

   ```bash
   git clone https://github.com/MIT-Emerging-Talent/ELO2-Smart-Pantry-Manager.git
   ```

2. **Navigate into the folder**

   ```bash
   cd smart_pantry_manager
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**

   ```bash
   streamlit run the_app/smart_pantry.py
   ```

Then open the local link displayed in your terminal — and enjoy your smart kitchen!

---

## 👩‍💻 Team

**MIT Emerging Talent – ELO2 Smart Pantry Manager Team** are:

* Azza Omer
* May Mon
* Omnia Mustafa
  
Built with teamwork, creativity, and a mission to make everyday life smarter and
more sustainable.

---

## 🌟 Vision

To make every kitchen **smarter, healthier, and more efficient** —
helping people use what they have before it goes to waste.
