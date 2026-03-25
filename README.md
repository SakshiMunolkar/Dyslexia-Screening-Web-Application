 🧠 Dyslexia Screening Web Application

 Overview
The Dyslexia Screening Web Application is an interactive tool designed to identify early signs of dyslexia by evaluating reading and writing abilities. The system conducts multiple tests and provides automated scoring along with a detailed report.

 🚀 Features
- 🔤 Character Recognition Test  
- 📖 Word Reading Test  
- 📝 Sentence Processing Test  
- 🖼️ Image-Based Handwriting Analysis  
- 🎤 Speech-to-Text Support (Audio Mode)  
- 📊 Automated Scoring System  
- 📄 PDF Report Generation with Risk Classification  


 🛠️ Technologies Used
- Python  
- Streamlit  
- SpeechRecognition  
- Pydub  
- OCR (Tesseract)  
- ReportLab  
- Pandas  

📂 Project Structure

project/
│── app.py
│── utils/
│ ├── data_loader.py
│ ├── ocr.py
│ ├── text_compare.py
│ ├── scoring.py
│ ├── logger.py
│ ├── pdf_generator.py
│── records.csv
│── requirements.txt
│── README.md


 ⚙️ Installation

 1. Clone Repository
bash
git clone https://github.com/your-username/dyslexia-screening-app.git
cd dyslexia-screening-app
pip install -r requirements.txt

▶️ Run the Application
streamlit run app.py

🧪 How It Works
Enter patient details
Select test mode (Text or Audio)
Complete the following stages:
Character Recognition
Word Reading
Sentence Processing
Image Text Recognition
System evaluates responses and calculates score
Generates downloadable PDF report with risk level

📊 Output
Accuracy Score (%)
Risk Level (Low / Medium / High)
Detailed PDF Report



