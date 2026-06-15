from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "report" / "COEN807_Technical_Report.pdf"
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = PROJECT_ROOT / "figures"
GITHUB_URL = "https://github.com/MusbahuTijjani/COEN807_Student_Performance_ML"


def register_fonts():
    try:
        pdfmetrics.registerFont(TTFont("TNR", r"C:\Windows\Fonts\times.ttf"))
        pdfmetrics.registerFont(TTFont("TNR-Bold", r"C:\Windows\Fonts\timesbd.ttf"))
        pdfmetrics.registerFont(TTFont("TNR-Italic", r"C:\Windows\Fonts\timesi.ttf"))
        return "TNR", "TNR-Bold", "TNR-Italic"
    except Exception:
        return "Times-Roman", "Times-Bold", "Times-Italic"


FONT, BOLD, ITALIC = register_fonts()


def styles():
    base = getSampleStyleSheet()
    base.add(
        ParagraphStyle(
            "CoverTitle",
            parent=base["Title"],
            fontName=BOLD,
            fontSize=17,
            leading=21,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceAfter=12,
        )
    )
    base.add(
        ParagraphStyle(
            "CoverText",
            parent=base["Normal"],
            fontName=FONT,
            fontSize=12,
            leading=16,
            alignment=TA_CENTER,
            spaceAfter=6,
        )
    )
    base.add(
        ParagraphStyle(
            "Heading1Clean",
            parent=base["Heading1"],
            fontName=BOLD,
            fontSize=13.5,
            leading=16,
            alignment=TA_LEFT,
            textColor=colors.black,
            spaceBefore=10,
            spaceAfter=5,
        )
    )
    base.add(
        ParagraphStyle(
            "Heading2Clean",
            parent=base["Heading2"],
            fontName=BOLD,
            fontSize=11.5,
            leading=14,
            alignment=TA_LEFT,
            textColor=colors.black,
            spaceBefore=8,
            spaceAfter=4,
        )
    )
    base.add(
        ParagraphStyle(
            "BodyClean",
            parent=base["BodyText"],
            fontName=FONT,
            fontSize=10.2,
            leading=13.5,
            alignment=TA_JUSTIFY,
            textColor=colors.black,
            spaceAfter=5,
        )
    )
    base.add(
        ParagraphStyle(
            "SmallClean",
            parent=base["BodyText"],
            fontName=FONT,
            fontSize=8.4,
            leading=10.5,
            alignment=TA_LEFT,
            textColor=colors.black,
            spaceAfter=2,
        )
    )
    base.add(
        ParagraphStyle(
            "Caption",
            parent=base["BodyText"],
            fontName=ITALIC,
            fontSize=8.5,
            leading=10.5,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceAfter=5,
        )
    )
    return base


STYLES = styles()


def p(text, style="BodyClean"):
    return Paragraph(escape(text), STYLES[style])


def h(text, level=1):
    return p(text, "Heading1Clean" if level == 1 else "Heading2Clean")


def bullets(items):
    story = []
    for item in items:
        story.append(p("- " + item))
    return story


def report_table(rows, widths=None, font_size=8.2):
    data = [[Paragraph(escape(str(cell)), STYLES["SmallClean"]) for cell in row] for row in rows]
    tbl = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9EEF5")),
                ("FONTNAME", (0, 0), (-1, 0), BOLD),
                ("FONTNAME", (0, 1), (-1, -1), FONT),
                ("FONTSIZE", (0, 0), (-1, -1), font_size),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#444444")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return tbl


def metric_rows(csv_name):
    df = pd.read_csv(RESULTS_DIR / csv_name)
    rows = [["Model", "Accuracy", "Bal. Acc.", "Precision", "Recall", "F1", "ROC-AUC", "TP", "FN", "FP"]]
    for _, row in df.iterrows():
        rows.append(
            [
                row["model"].replace("_", " "),
                f"{row['accuracy']:.3f}",
                f"{row['balanced_accuracy']:.3f}",
                f"{row['precision_at_risk']:.3f}",
                f"{row['recall_at_risk']:.3f}",
                f"{row['f1_at_risk']:.3f}",
                f"{row['roc_auc']:.3f}",
                int(row["tp"]),
                int(row["fn"]),
                int(row["fp"]),
            ]
        )
    return rows


def add_image(path, width=5.9 * inch):
    img = Image(str(path))
    ratio = img.imageHeight / img.imageWidth
    img.drawWidth = width
    img.drawHeight = width * ratio
    img.hAlign = "CENTER"
    return img


def page_num(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT, 9)
    canvas.drawCentredString(A4[0] / 2, 0.35 * inch, str(doc.page))
    canvas.restoreState()


def build():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(REPORT_PATH),
        pagesize=A4,
        leftMargin=0.72 * inch,
        rightMargin=0.72 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.62 * inch,
    )
    story = []

    story.append(Spacer(1, 1.15 * inch))
    story.append(p("COEN807 TERM PROJECT TECHNICAL REPORT", "CoverTitle"))
    story.append(
        p(
            "Predicting At-Risk Student Academic Performance Using Machine Learning: "
            "A Comparative Study of Supervised Classification Models",
            "CoverTitle",
        )
    )
    story.append(Spacer(1, 0.18 * inch))
    story.append(p("Course Code: COEN807", "CoverText"))
    story.append(p("Course Title: Machine Learning", "CoverText"))
    story.append(p("Student Name: Musbahu Tijjani", "CoverText"))
    story.append(p("Registration Number: P25EGCP8009", "CoverText"))
    story.append(p("Lecturer: Dr. Y. Ibrahim", "CoverText"))
    story.append(p("GitHub Repository: " + GITHUB_URL, "CoverText"))
    story.append(p("Submission Deadline: June 21, 2026", "CoverText"))
    story.append(PageBreak())

    story.append(h("Abstract"))
    story.append(
        p(
            "This project applies supervised machine learning to predict students who may be at risk of failing a final course grade. "
            "The study uses the public UCI Student Performance dataset, specifically the Portuguese language course subset with 649 records. "
            "The target variable was engineered as At_Risk = 1 when the final grade G3 is below 10 out of 20. Two experimental settings were compared: "
            "an early-warning setting that excludes prior period grades G1 and G2, and a performance-aware setting that includes them. Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, Support Vector Machine, and a Dummy Majority baseline were implemented using reproducible preprocessing pipelines and grid-search tuning. "
            "The best early-warning model was Random Forest, achieving 0.800 recall and 0.582 F1 for at-risk students. The best performance-aware model was Support Vector Machine, achieving 0.908 accuracy, 0.850 recall, 0.739 F1, and 0.936 ROC-AUC. "
            "The results show that prior academic performance improves prediction, but the early-warning model remains useful because it can support intervention before later grades are available."
        )
    )

    story.append(h("1. Introduction and Problem Definition"))
    story.append(
        p(
            "Educational institutions often need to identify students who require academic support before final examinations. A purely reactive approach, where support is offered only after students fail, is inefficient and unfair to learners who could have benefited from earlier intervention. "
            "The real-world problem addressed in this project is therefore the prediction of at-risk students from demographic, family, school, and behavioural attributes. The task is formulated as binary supervised classification."
        )
    )
    story.extend(
        bullets(
            [
                "Objective 1: build a reproducible machine learning pipeline for predicting At_Risk students.",
                "Objective 2: compare multiple classification algorithms under the same experimental protocol.",
                "Objective 3: evaluate models using metrics that prioritise detection of at-risk students rather than accuracy alone.",
                "Objective 4: critically discuss limitations, bias, ethical use, and practical deployment concerns.",
            ]
        )
    )

    story.append(h("2. Dataset Description and Justification"))
    story.append(
        p(
            "The dataset was sourced from the UCI Machine Learning Repository. It contains student achievement data collected from two Portuguese secondary schools and includes demographic, social, school-related, behavioural, and academic attributes. "
            "This project uses the Portuguese language course subset because it has 649 records, making it larger than the Mathematics subset. The original output variable is G3, the final grade on a 0-20 scale. For this project, students with G3 below 10 were labelled At_Risk."
        )
    )
    story.append(
        report_table(
            [
                ["Dataset property", "Value"],
                ["Source", "UCI Machine Learning Repository - Student Performance dataset"],
                ["Selected file", "student-por.csv"],
                ["Records", "649 students"],
                ["Original columns", "33 variables"],
                ["Target engineering", "At_Risk = 1 if G3 < 10, otherwise 0"],
                ["Class distribution", "100 at-risk students and 549 not-at-risk students"],
                ["Missing values", "0 missing values in the selected file"],
            ],
            widths=[1.9 * inch, 4.6 * inch],
        )
    )
    story.append(Spacer(1, 4))
    story.append(add_image(FIGURES_DIR / "class_distribution.png", width=4.7 * inch))
    story.append(p("Figure 1: Class distribution showing the imbalance between at-risk and not-at-risk students.", "Caption"))
    story.append(
        p(
            "The dataset is suitable for the project because it is public, credible, tabular, ethically discussable, and directly related to an educational decision-support problem. "
            "Its imbalance also creates a realistic evaluation challenge: a model can achieve high accuracy by predicting the majority class, while still failing to identify the students who need support."
        )
    )

    story.append(h("3. Data Preprocessing and Feature Engineering"))
    story.append(
        p(
            "The preprocessing pipeline was implemented using scikit-learn ColumnTransformer and Pipeline objects so that all transformations are fitted only on training data and then applied to validation or test data. "
            "Categorical variables were encoded using one-hot encoding with unknown-category handling, while numerical variables were imputed by median and standardised. Although the selected file has no missing values, explicit imputation improves robustness and reproducibility."
        )
    )
    story.extend(
        bullets(
            [
                "Target variable: At_Risk = 1 when G3 < 10, representing a final failing grade.",
                "Early-warning feature set: excludes G1 and G2 so the model relies only on information available before later performance records.",
                "Performance-aware feature set: includes G1 and G2 to estimate the improvement obtained when prior grades are available.",
                "Train-test split: 80% training and 20% testing with stratification to preserve the class ratio.",
                "Class imbalance handling: class_weight='balanced' was used where supported by the model.",
            ]
        )
    )

    story.append(h("4. Methodology and Model Selection"))
    story.append(
        p(
            "Six classifiers were implemented: Dummy Majority, Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, and Support Vector Machine. "
            "The Dummy Majority classifier is included as a baseline because the dataset is imbalanced. Logistic Regression provides an interpretable linear baseline, Decision Tree provides rule-based interpretability, Random Forest and Gradient Boosting represent ensemble tree methods, and SVM provides a strong margin-based nonlinear classifier."
        )
    )
    story.append(
        KeepTogether(
            [
                report_table(
                    [
                        ["Model", "Reason for inclusion", "Main tuned parameters"],
                        ["Dummy Majority", "Baseline for class imbalance", "None"],
                        ["Logistic Regression", "Interpretable linear classifier", "C"],
                        ["Decision Tree", "Rule-based nonlinear model", "max_depth, min_samples_leaf"],
                        ["Random Forest", "Robust ensemble model", "n_estimators, max_depth, min_samples_leaf"],
                        ["Gradient Boosting", "Sequential ensemble model", "n_estimators, learning_rate, max_depth"],
                        ["Support Vector Machine", "Margin-based classifier", "C, kernel"],
                    ],
                    widths=[1.45 * inch, 3.0 * inch, 2.05 * inch],
                )
            ]
        )
    )

    story.append(h("5. Experimental Design"))
    story.append(
        p(
            "The experimental design used two controlled experiments with the same train-test split and the same model family list. Hyperparameters were tuned using five-fold stratified cross-validation on the training set only. "
            "The final reported metrics were then computed once on the untouched test set. The tuning score was F1 for the at-risk class, because both missing at-risk students and over-flagging not-at-risk students have practical costs."
        )
    )
    story.extend(
        bullets(
            [
                "Primary metric: F1-score for the At_Risk class.",
                "Safety metric: recall for the At_Risk class, because false negatives mean unsupported students.",
                "Comparison metrics: accuracy, balanced accuracy, precision, ROC-AUC, and confusion matrix counts.",
                "Reproducibility: fixed random seed, saved source code, saved results, saved figures, and README instructions.",
            ]
        )
    )

    story.append(h("6. Results and Evaluation"))
    story.append(h("6.1 Early-Warning Experiment Without G1 and G2", 2))
    story.append(
        p(
            "In the early-warning setting, prior period grades were excluded. This makes the problem harder but more useful for earlier intervention. "
            "The Random Forest model achieved the best F1-score for the at-risk class, with recall of 0.800 and F1 of 0.582. The Dummy Majority model achieved high accuracy because most students are not at risk, but it detected no at-risk students."
        )
    )
    story.append(
        report_table(
            metric_rows("metrics_early_warning_without_prior_grades.csv"),
            widths=[1.55 * inch, 0.55 * inch, 0.58 * inch, 0.62 * inch, 0.55 * inch, 0.50 * inch, 0.58 * inch, 0.32 * inch, 0.32 * inch, 0.32 * inch],
            font_size=7.6,
        )
    )
    story.append(Spacer(1, 4))
    story.append(add_image(FIGURES_DIR / "model_comparison_early_warning_without_prior_grades.png", width=5.6 * inch))
    story.append(p("Figure 2: Early-warning model comparison using recall, F1-score, and ROC-AUC.", "Caption"))

    story.append(h("6.2 Performance-Aware Experiment With G1 and G2", 2))
    story.append(
        p(
            "Including prior grades G1 and G2 improved model performance, which is expected because earlier grades are strong predictors of final grade. "
            "The best F1-score was achieved by the Support Vector Machine, with 0.908 accuracy, 0.850 recall for at-risk students, 0.739 F1, and 0.936 ROC-AUC. Logistic Regression achieved the highest at-risk recall of 0.900 but with lower precision."
        )
    )
    story.append(
        report_table(
            metric_rows("metrics_performance_aware_with_prior_grades.csv"),
            widths=[1.55 * inch, 0.55 * inch, 0.58 * inch, 0.62 * inch, 0.55 * inch, 0.50 * inch, 0.58 * inch, 0.32 * inch, 0.32 * inch, 0.32 * inch],
            font_size=7.6,
        )
    )
    story.append(Spacer(1, 4))
    story.append(add_image(FIGURES_DIR / "model_comparison_performance_aware_with_prior_grades.png", width=5.6 * inch))
    story.append(p("Figure 3: Performance-aware comparison after adding prior grade features.", "Caption"))

    story.append(h("7. Comparative Analysis and Discussion"))
    story.append(
        p(
            "The experiment shows a clear trade-off between early usefulness and predictive strength. The early-warning Random Forest model is less accurate than the performance-aware SVM, but it can be used before later academic grades are available. "
            "The performance-aware setting is better for prediction because G1 and G2 contain direct evidence of academic progress, but it may identify risk later than desired. This difference is important for practical deployment: if the purpose is early intervention, the early-warning model may be more valuable despite lower F1-score."
        )
    )
    story.append(
        p(
            "Accuracy alone is misleading. The Dummy Majority baseline achieved 0.846 accuracy in both settings while detecting zero at-risk students. This confirms that recall, F1-score, balanced accuracy, ROC-AUC, and confusion matrices are essential for imbalanced educational prediction."
        )
    )
    story.append(
        p(
            "The confusion matrices indicate that the early-warning Random Forest found 16 of 20 at-risk students in the test set but incorrectly flagged 19 not-at-risk students. In a real tutoring programme, such false positives may be acceptable if support resources are available and intervention is non-punitive. "
            "The performance-aware SVM found 17 of 20 at-risk students and reduced false positives to 9, showing better precision once grade history is included."
        )
    )

    story.append(h("8. Limitations, Biases, and Lessons Learned"))
    story.append(
        p(
            "The main limitation is external validity. The data were collected from Portuguese secondary schools and may not represent Nigerian schools, universities, or other educational systems. "
            "The dataset is also modest in size and includes sensitive socioeconomic and family variables that may encode inequality. A model trained on such variables could unintentionally reproduce social bias if used for punishment, ranking, or exclusion."
        )
    )
    story.extend(
        bullets(
            [
                "Bias risk: features such as parental education, address type, internet access, and family support may act as proxies for socioeconomic inequality.",
                "Measurement limitation: student motivation, teaching quality, mental health, insecurity, and school resources are not fully captured.",
                "Deployment limitation: model performance should be validated on local data before use in a different country or institution.",
                "Ethical lesson: the model should allocate support and tutoring, not punish students or label them permanently.",
            ]
        )
    )

    story.append(h("9. Conclusion and Future Work"))
    story.append(
        p(
            "This project demonstrates an end-to-end supervised learning workflow for predicting at-risk students using a public education dataset. The early-warning Random Forest model detected 80% of at-risk students without using prior grade variables, while the performance-aware SVM achieved stronger overall performance when G1 and G2 were included. "
            "The strongest practical conclusion is that machine learning can support educational intervention, but only when evaluation metrics, fairness, transparency, and human oversight are treated as central design requirements."
        )
    )
    story.append(
        p(
            "Future work should validate the approach on Nigerian educational data, collect richer contextual variables, compare calibration methods, test threshold tuning for different tutoring capacities, and audit subgroup performance across gender, location, school type, and socioeconomic groups."
        )
    )

    story.append(h("10. Reproducibility and Repository"))
    story.append(
        p(
            "The project folder contains source code, data access files, processed dataset, trained models, results, figures, report, slides, requirements, and a README file. "
            "The GitHub repository link to include in the final submission is: " + GITHUB_URL + ". If the repository is created under a different account or name, this link should be updated in both the report and slides before submission."
        )
    )

    story.append(h("References"))
    story.append(
        p(
            "Cortez, P., & Silva, A. (2008). Using data mining to predict secondary school student performance. Proceedings of the 5th FUture BUsiness TEChnology Conference."
        )
    )
    story.append(
        p(
            "UCI Machine Learning Repository. (n.d.). Student Performance dataset. https://archive.ics.uci.edu/dataset/320/student+performance"
        )
    )
    story.append(
        p(
            "Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. Journal of Machine Learning Research, 12, 2825-2830."
        )
    )

    doc.build(story, onFirstPage=page_num, onLaterPages=page_num)
    print(REPORT_PATH)


if __name__ == "__main__":
    build()
