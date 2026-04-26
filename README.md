# Skin Condition Detection Smart Mirror

## Project Overview

This project explores **fair and accurate facial skin condition detection** using computer vision, with a particular focus on **performance across diverse skin tones**, especially darker skin. The system is designed as the backend intelligence for a proposed *AI-powered smart mirror* that can analyze live camera input, identify visible skin conditions, and provide interpretable feedback.

The core research question is:

> *How do dataset diversity, class balance, and color information affect the performance and fairness of skin condition classification models?*

---

## Key Goals

* Build a real-time skin condition classifier using **PyTorch**
* Evaluate bias and skew caused by **imbalanced and non-diverse datasets**
* Compare model behavior on **diverse vs. non-diverse datasets**
* Reduce skin-tone bias using **grayscale preprocessing**
* Improve transparency using **Grad-CAM visual explanations**

---

## Datasets Used

### 1. Google SCIN Dataset

* Large-scale dermatology image dataset
* Image metadata split across:

  * `scin_cases.csv` (image paths)
  * `scin_labels.csv` (conditions)
* Required joining files to correctly map labels to images
* Limited representation of darker skin tones

### 2. Custom / External Diverse Dataset (Applied Access)

* Dataset trained on darker-skinned individuals
* Used to evaluate fairness and reduce skew

### 3. Custom Collected Dataset (Planned)

* Images voluntarily collected from university participants
* Focus on darker skin tones and underrepresented conditions
* Used strictly for academic research

---

## Skin Conditions Considered

* Acne
* Clear / No visible condition
* Post-inflammatory hyperpigmentation
* Dark circles

(Classes were narrowed during experimentation to improve stability and accuracy.)

---

## Model Architecture

* **MobileNetV2** (pretrained on ImageNet)
* Fine-tuned using **transfer learning**
* Final classifier layer replaced to match number of skin condition classes

### Why MobileNetV2?

* Lightweight and efficient
* Suitable for real-time webcam inference
* Strong baseline for image classification tasks

---

## Training Pipeline

* Framework: **PyTorch**
* Input size: `224 × 224`
* Loss function: `CrossEntropyLoss` with **class weighting**
* Optimizer: `Adam`
* Learning rate scheduling: `ReduceLROnPlateau`

### Data Augmentation

* Horizontal flipping
* Resize normalization

### Grayscale Experiment

* RGB images converted to grayscale (3-channel)
* Purpose:

  * Reduce reliance on skin tone
  * Encourage focus on texture and lesion patterns
* Performance compared between:

  * RGB vs. grayscale
  * Diverse vs. non-diverse datasets

---

## Evaluation Metrics

* Classification Accuracy
* **F1 Score** (to handle class imbalance)
* Confusion Matrix
* Fairness comparisons across skin tone groups

These metrics were used to identify skew such as:

* Model predicting acne for nearly all inputs
* Hyperpigmentation over-prediction on darker skin

---

## Real-Time Webcam Inference

* Live video capture using **OpenCV**
* Each frame:

  1. Preprocessed (resize, normalize, optional grayscale)
  2. Passed through trained model
  3. Softmax confidence computed

### Confidence Thresholding

* Predictions below a confidence threshold return **"Unsure"**
* Prevents misleading or overconfident outputs

---

## Model Interpretability (Grad-CAM) ** NOT INCLUDED IN REPO **

* Integrated **Grad-CAM** for visual explanations
* Highlights regions the model focuses on when predicting
* Used to verify whether the model attends to:

  * Skin lesions vs. background
  * Face-wide features vs. localized regions

Grad-CAM was adapted to work with:

* MobileNetV2
* Live webcam frames

---

## Bias & Fairness Findings

* Models trained on skewed datasets learned **skin tone shortcuts**
* Over-association between darker skin and hyperpigmentation
* Improved behavior observed when:

  * Using grayscale preprocessing
  * Introducing dataset diversity
  * Applying class balancing

This demonstrates a **real-world AI fairness problem** with technical and ethical implications.

---

## Planned Extensions

* Integrate ChatGPT API to:

  * Explain predictions in natural language
  * Combine visual detection with user-reported symptoms
  * Provide non-diagnostic educational feedback

* UI development for smart mirror display:

  * Confidence indicators
  * Highlighted regions
  * Skin care insights
 
* LED Screen & Raspberry PI Integration:
  * Details TBD

---

## Tools & Technologies

* Python
* PyTorch
* Torchvision
* OpenCV
* Grad-CAM
* NumPy
* Google Forms (data collection)

---

## Ethical Considerations

* No medical diagnosis claims
* Explicit consent for image collection
* Transparency around data usage
* Focus on fairness and harm reduction

---

## Status

**Active Research / Development Project**

This project is being developed as both a **technical AI system** and a **research investigation into fairness in computer vision**.

---

## Authors

Developed by student researchers exploring ethical, fair, and explainable AI systems for real-world applications.
