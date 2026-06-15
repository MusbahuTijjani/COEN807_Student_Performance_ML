# COEN807 Term Project

## Project Title

Predicting At-Risk Student Academic Performance Using Machine Learning: A Comparative Study of Supervised Classification Models

## Student Information

- Name: Musbahu Tijjani
- Registration Number: P25EGCP8009
- Course Code: COEN807
- Course Title: Machine Learning

## GitHub Repository

Placeholder repository link:
https://github.com/MusbahuTijjani/COEN807_Student_Performance_ML

Update this link in the report and slides if the final GitHub repository uses a different URL.

## Project Overview

This project predicts whether a student is at risk of failing based on the UCI Student Performance dataset. The selected target is:

`At_Risk = 1 if G3 < 10, otherwise 0`

Two experiments are implemented:

1. Early-warning experiment without prior grades `G1` and `G2`.
2. Performance-aware experiment with prior grades `G1` and `G2`.

The project compares Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, Support Vector Machine, and a Dummy Majority baseline.

## Dataset

Source: UCI Machine Learning Repository, Student Performance dataset  
URL: https://archive.ics.uci.edu/dataset/320/student+performance

Selected file:

`data/raw/student/student-por.csv`

The dataset contains 649 Portuguese language course records. The processed file with the engineered target is saved as:

`data/student_performance_portuguese_with_target.csv`

## Folder Structure

- `src/`: source code for training and report generation
- `data/`: raw and processed dataset files
- `results/`: CSV and JSON result summaries
- `figures/`: generated evaluation plots
- `models/`: saved best models
- `report/`: final technical report PDF
- `slides/`: final PowerPoint presentation

## Reproduce the Results

Create and activate a Python environment, then run:

```bash
pip install -r requirements.txt
python src/train_models.py
```

Optional: regenerate the report after the model outputs exist:

```bash
python src/build_report.py
```

## Main Results

Early-warning experiment without `G1` and `G2`:

- Best model: Random Forest
- At-risk recall: 0.800
- At-risk F1-score: 0.582
- ROC-AUC: 0.822

Performance-aware experiment with `G1` and `G2`:

- Best model: Support Vector Machine
- Accuracy: 0.908
- At-risk recall: 0.850
- At-risk F1-score: 0.739
- ROC-AUC: 0.936

## Submission Note

Before submission:

- Upload this project folder to Google Drive.
- Set folder permission to `Anyone with the link can view`.
- Confirm the GitHub repository is public or accessible.
- Confirm the GitHub link appears in both the report and presentation slides.
- Submit the Google Drive folder link through the lecturer's form.
