# 🩺 DiseaScan

### AI-Powered Disease Detection System

*Making healthcare faster, more accessible, and more proactive.*


> ⚠️ **Disclaimer:** DiseaScan is intended for educational and preliminary screening purposes only. It does not substitute professional medical diagnosis or advice. Always consult a qualified healthcare provider.

---

## 📌 Overview

**DiseaScan** is a full-stack AI application that analyzes medical images and predicts the **top 3 most probable diseases along with confidence scores** — giving users a transparent, reliable first layer of health screening.

Unlike traditional single-output diagnostic tools, DiseaScan surfaces multiple ranked predictions, reducing over-reliance on any single result. The system is built to be simple enough for anyone to use — regardless of technical or medical background — making early disease detection accessible to all, including those in remote or underserved regions.

---

## ✨ Key Features

| Feature | Description |
|--------|-------------|
| 🔬 **Deep Learning Diagnosis** | Fine-tuned CNN model built with Keras & TensorFlow for accurate image-based disease detection |
| 📊 **Top-3 Predictions + Confidence** | Returns the 3 most probable diseases with confidence scores for transparent, multi-hypothesis output |
| 🖼️ **Medical Image Upload** | Clean UI for uploading medical images (X-rays, scans, etc.) with instant results |
| ⚡ **Real-Time Analysis** | Backend processes and returns predictions in real time |
| 🌍 **Accessibility-First Design** | Designed for users with zero technical/medical knowledge — a few clicks is all it takes |
| 🧠 **Transfer Learning** | Leverages pre-trained architectures fine-tuned on medical datasets for improved performance |

---

## 🗂️ Project Structure

```
DiseaScan/
│
├── DISEASCAN/                    # Core AI model & training pipeline
│   ├── model/                    # Saved fine-tuned deep learning model
│   ├── dataset/                  # Medical image datasets
│   └── notebooks/                # Training, evaluation & experimentation notebooks
│
├── DISEASCAN_Backend/            # Flask REST API
│   ├── app.py                    # Main application entry point & API routes
│   ├── predict.py                # Inference logic — loads model & returns top-3 predictions
│   └── requirements.txt          # Python dependencies
│
└── DISEASCAN_Frontend/           # Static web frontend
    ├── index.html                # Main UI — image upload & results display
    └── static/                   # CSS, JS, and image assets
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI / ML** | TensorFlow, Keras, Transfer Learning |
| **Data Processing** | NumPy, Pandas, OpenCV / PIL |
| **Backend** | Python, Flask |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Model Serialization** | Keras `.h5` / SavedModel format |

---

## ⚙️ How It Works

```
                    ┌─────────────────────────────────┐
                    │         User Interface           │
                    │   Upload Medical Image (e.g.     │
                    │   photo)                         │
                    └────────────┬────────────────────┘
                                 │  HTTP POST
                    ┌────────────▼────────────────────┐
                    │         Flask Backend            │
                    │   Preprocess input image         │
                    │   Normalize & resize for model   │
                    └────────────┬────────────────────┘
                                 │  Model Inference
                    ┌────────────▼────────────────────┐
                    │    Fine-Tuned Deep Learning      │
                    │    Model (Keras + TensorFlow)    │
                    │    Extracts features & patterns  │
                    └────────────┬────────────────────┘
                                 │  JSON Response
                    ┌────────────▼────────────────────┐
                    │       Results Displayed          │
                    │     Disease 1 — 91.4% confident  │
                    │     Disease 2 —  6.2% confident  │
                    │     Disease 3 —  2.4% confident  │
                    └─────────────────────────────────┘
```

---

## 🧠 The AI Model

DiseaScan's prediction engine is a **fine-tuned Convolutional Neural Network (CNN)** trained on labeled medical image data.

- **Framework:** Keras + TensorFlow
- **Approach:** Transfer learning — a pre-trained model is fine-tuned on domain-specific medical data, allowing the network to leverage general visual features while adapting to disease-specific patterns
- **Output:** Softmax layer returning probability scores across all disease classes; top 3 are surfaced to the user
- **Input:** Preprocessed and normalized medical images (resized to model input dimensions)

> The model is continuously being improved through better data curation, class balancing, and hyperparameter optimization.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation & Run

```bash
# 1. Clone the repository
git clone https://github.com/Saurav-SS71/DiseaScan.git
cd DiseaScan

# 2. Install backend dependencies
cd DISEASCAN_Backend
pip install -r requirements.txt

# 3. Start the Flask server
python app.py
```

Then open `DISEASCAN_Frontend/index.html` in your browser:


---


## 🎯 Why DiseaScan?

Many serious diseases become critical only because they are caught too late. DiseaScan acts as an intelligent **first layer of screening** — providing instant preliminary insights that encourage users to seek timely professional care.

This matters most for:

- 🏥 **Regions with limited healthcare access** — where doctor visits are expensive or time-consuming
- 👩‍💻 **Non-technical users** — the UI requires no medical or technical expertise
- ⏱️ **Early detection** — faster action leads to significantly better health outcomes

---

## 🔮 Roadmap

- [ ] Expand model to cover more disease categories
- [ ] Add report generation (PDF export of predictions)
- [ ] Integrate nearest hospital locator via Maps API
- [ ] Cloud deployment (AWS / GCP / Render)
- [ ] Mobile-responsive UI
- [ ] User authentication and prediction history

---

## ⚠️ Limitations

DiseaScan is an evolving system. Known challenges include:

- Predictions may be inaccurate for rare diseases with limited training data
- Model performance can vary with image quality and resolution
- Class imbalance in training data may affect confidence score calibration

These are actively being addressed through ongoing model improvements and dataset augmentation.

---

## 👤 Author

**Saurav**  
B.Tech Mathematics & Computing — Delhi Technological University (DTU)

[![GitHub](https://img.shields.io/badge/GitHub-Saurav--SS71-181717?style=flat-square&logo=github)](https://github.com/Saurav-SS71)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---
