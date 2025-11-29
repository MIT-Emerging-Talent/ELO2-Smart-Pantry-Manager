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
👉 [Smart Pantry Manager – Web App](https://smart-pantry-manager.streamlit.app/)

---

## 💡 Why this App?

Have you ever bought food, put it in the pantry, and then forgot about it?
Sometimes it goes bad before you can use it. Meanwhile, some people don’t have enough to eat.

With busy lives, work pressure, and rushing around, it’s hard to decide what to cook.
Kids don’t want the same meals every day—they want variety.

**Smart Pantry Manager** helps solve these everyday problems by:

- Tracking items in your pantry  
- Alerting you before products expire  
- Suggesting recipes based on what you already have  
- Helping you add more variety to your meals without extra effort  

It works as your smart kitchen assistant — reducing waste, saving money, and simplifying cooking.

---

## 🧩 Project Development Stages

### ✅ Stage 1: Adding Products & Expiry Alerts *(Completed)*

- Built interface to add pantry items + expiry dates  
- Stored pantry data in CSV  
- Created expiry alerts  
- Added basic UI & pantry summary

🎯 **Result:** Solid foundation for tracking pantry items and preventing waste.

---

### ✅ Stage 2: Recipe Recommendations *(Completed)*

- Added full recipe database  
- Matched pantry items with recipe ingredients  
- Displayed recipe recommendations with a clean UI  
- Added fuzzy matching and improved ingredient mapping  
- Integrated SQLite for storing recipes

🎯 **Result:** Smart, accurate recipe suggestions using available ingredients.

---

### ✅ Stage 3: Custom Ingredient Selection & UI Enhancements *(Completed)*

- Added **“Search Recipes”** page  
- Added **“All Recipes”** page with full list + filtering  
- Added **manual ingredient selection**  
- Improved layout, spacing, and readability  
- Reorganized code structure into modules  
- Added **loading states**, better error handling  
- Improved pantry table formatting  
- Updated navigation and sidebar UI

🎯 **Result:** Faster, cleaner, and more user-friendly experience.

---

## 🔜 Stage 4: Healthy Eating Mode *(Planned)*

- “Healthy Recipes Only” filter  
- Nutrition + calorie tags  
- Categories like *High Protein*, *Vegetarian*, *Low Fat*  

---

## 🤖 Stage 5: Smart Camera & AI Features *(Future)*

- Scan items with phone camera  
- AI detection of product name + expiry date  
- Behavioral recommendations  
- Cloud sync & multi-device login  

---

## 🔧 Tools & Technologies

| Tool | Purpose |
|------|---------|
| **Python** | Core logic |
| **Streamlit** | Web app UI |
| **Pandas** | Data processing |
| **SQLite** | Recipe & ingredient data |
| **CSV** | Local pantry storage |
| **OpenAI / Vision AI** | Future AI automation |
| **GitHub CI + Linting** | Code quality & consistency |

---

## 🚀 Additional Work Completed

- Migrated recipes from **CSV → SQLite**  
- Added **All Recipes** page  
- Added **Search Recipes** page  
- Improved ingredient parsing  
- Added keyword search for titles + ingredients  
- Improved recipe recommendation accuracy  
- UI polishing across pages  
- Bug fixes + performance improvements

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

- Azza Omer
- May Mon
- Omnia Mustafa
  
Built with teamwork, creativity, and a mission to make everyday life smarter and
more sustainable.

---

## 🌟 Vision

To make every kitchen **smarter, healthier, and more efficient** —
helping people use what they have before it goes to waste.
