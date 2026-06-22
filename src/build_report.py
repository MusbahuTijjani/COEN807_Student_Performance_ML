from csv import DictReader
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.shapes import Drawing
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
ASSETS_DIR = PROJECT_ROOT / "assets"

NAME = "Musbahu Tijjani"
REG_NO = "P25EGCP8009"
COURSE_CODE = "COEN807"
COURSE_TITLE = "Machine Learning"
LECTURER = "Dr. Y. Ibrahim"
GITHUB_URL = "https://github.com/MusbahuTijjani/COEN807_Student_Performance_ML"
PROJECT_TITLE = (
    "Predicting At-Risk Student Academic Performance Using Machine Learning: "
    "A Comparative Study of Supervised Classification Models"
)

FONT = "Times-Roman"
BOLD = "Times-Bold"
ITALIC = "Times-Italic"
FONTS_REGISTERED = False


def register_fonts():
    global FONT, BOLD, ITALIC, FONTS_REGISTERED
    if FONTS_REGISTERED:
        return
    font_dir = Path(r"C:\Windows\Fonts")
    regular = font_dir / "times.ttf"
    bold = font_dir / "timesbd.ttf"
    italic = font_dir / "timesi.ttf"
    if regular.exists() and bold.exists() and italic.exists():
        pdfmetrics.registerFont(TTFont("TimesNewRoman", str(regular)))
        pdfmetrics.registerFont(TTFont("TimesNewRoman-Bold", str(bold)))
        pdfmetrics.registerFont(TTFont("TimesNewRoman-Italic", str(italic)))
        FONT = "TimesNewRoman"
        BOLD = "TimesNewRoman-Bold"
        ITALIC = "TimesNewRoman-Italic"
    FONTS_REGISTERED = True


def styles():
    register_fonts()
    return {
        "cover": ParagraphStyle(
            "cover",
            fontName=BOLD,
            fontSize=12,
            leading=16,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceAfter=0,
        ),
        "h1": ParagraphStyle(
            "h1",
            fontName=BOLD,
            fontSize=12,
            leading=24,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "h2",
            fontName=BOLD,
            fontSize=12,
            leading=24,
            alignment=TA_LEFT,
            textColor=colors.black,
            spaceBefore=7,
            spaceAfter=3,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "body",
            fontName=FONT,
            fontSize=12,
            leading=24,
            firstLineIndent=0.5 * inch,
            alignment=TA_LEFT,
            textColor=colors.black,
            spaceAfter=4,
        ),
        "body0": ParagraphStyle(
            "body0",
            fontName=FONT,
            fontSize=12,
            leading=24,
            alignment=TA_LEFT,
            textColor=colors.black,
            spaceAfter=4,
        ),
        "table_number": ParagraphStyle(
            "table_number",
            fontName=FONT,
            fontSize=12,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceBefore=10,
            spaceAfter=2,
            keepWithNext=True,
        ),
        "table_title": ParagraphStyle(
            "table_title",
            fontName=FONT,
            fontSize=12,
            leading=16,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceAfter=8,
            keepWithNext=True,
        ),
        "table_caption": ParagraphStyle(
            "table_caption",
            fontName=FONT,
            fontSize=12,
            leading=16,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceBefore=10,
            spaceAfter=8,
            keepWithNext=True,
        ),
        "figure_number": ParagraphStyle(
            "figure_number",
            fontName=BOLD,
            fontSize=12,
            leading=14,
            alignment=TA_LEFT,
            textColor=colors.black,
            spaceBefore=10,
            spaceAfter=2,
            keepWithNext=True,
        ),
        "figure_title": ParagraphStyle(
            "figure_title",
            fontName=ITALIC,
            fontSize=12,
            leading=16,
            alignment=TA_LEFT,
            textColor=colors.black,
            spaceAfter=8,
            keepWithNext=True,
        ),
        "figure_caption": ParagraphStyle(
            "figure_caption",
            fontName=FONT,
            fontSize=12,
            leading=16,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "figure_note": ParagraphStyle(
            "figure_note",
            fontName=FONT,
            fontSize=12,
            leading=16,
            alignment=TA_LEFT,
            textColor=colors.black,
            spaceBefore=6,
            spaceAfter=10,
        ),
        "table": ParagraphStyle(
            "table",
            fontName=FONT,
            fontSize=12,
            leading=14,
            alignment=TA_LEFT,
            textColor=colors.black,
        ),
        "table_bold": ParagraphStyle(
            "table_bold",
            fontName=BOLD,
            fontSize=12,
            leading=14,
            alignment=TA_LEFT,
            textColor=colors.black,
        ),
        "ref": ParagraphStyle(
            "ref",
            fontName=FONT,
            fontSize=12,
            leading=24,
            leftIndent=0.5 * inch,
            firstLineIndent=-0.5 * inch,
            textColor=colors.black,
            spaceAfter=2,
        ),
    }


STYLES = styles()


def para(text, style="body"):
    return Paragraph(escape(text), STYLES[style])


def h1(story, text):
    story.append(para(text, "h1"))


def h2(story, text):
    story.append(para(text, "h2"))


def bullet(story, text):
    story.append(para("- " + text, "body0"))


def add_table(story, headers, rows, widths=None, number=None, title=None, numeric_columns=False):
    data = [[Paragraph(escape(str(cell)), STYLES["table_bold"]) for cell in headers]]
    for row in rows:
        data.append([Paragraph(escape(str(cell)), STYLES["table"]) for cell in row])
    table = Table(data, colWidths=widths, hAlign="CENTER", repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), BOLD),
                ("FONTNAME", (0, 1), (-1, -1), FONT),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("LEADING", (0, 0), (-1, -1), 14),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LINEABOVE", (0, 0), (-1, 0), 0.8, colors.black),
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
                ("LINEBELOW", (0, -1), (-1, -1), 0.8, colors.black),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    if numeric_columns:
        table.setStyle(TableStyle([("ALIGN", (1, 0), (-1, -1), "CENTER")]))
    block = []
    caption_parts = []
    if number is not None:
        caption_parts.append(f"Table {number}.")
    if title:
        caption_parts.append(escape(title))
    if caption_parts:
        block.append(Paragraph(" ".join(caption_parts), STYLES["table_caption"]))
    block.append(table)
    story.append(KeepTogether(block))
    story.append(Spacer(1, 8))


def metric_rows(csv_name):
    rows = []
    with open(RESULTS_DIR / csv_name, newline="", encoding="utf-8") as handle:
        for row in DictReader(handle):
            rows.append(
                [
                    row["model"].replace("_", " "),
                    f"{float(row['accuracy']):.3f}",
                    f"{float(row['precision_at_risk']):.3f}",
                    f"{float(row['recall_at_risk']):.3f}",
                    f"{float(row['f1_at_risk']):.3f}",
                    f"{float(row['roc_auc']):.3f}",
                ]
            )
    return rows


def metric_chart(csv_name):
    models = []
    recall = []
    f1 = []
    roc_auc = []
    with open(RESULTS_DIR / csv_name, newline="", encoding="utf-8") as handle:
        for row in DictReader(handle):
            model = row["model"].replace("_", " ")
            models.append("SVM" if model == "Support Vector Machine" else model)
            recall.append(float(row["recall_at_risk"]))
            f1.append(float(row["f1_at_risk"]))
            roc_auc.append(float(row["roc_auc"]))

    drawing = Drawing(468, 310)
    chart = HorizontalBarChart()
    chart.x = 145
    chart.y = 55
    chart.width = 295
    chart.height = 220
    chart.data = [recall, f1, roc_auc]
    chart.categoryAxis.categoryNames = models
    chart.categoryAxis.labels.fontName = FONT
    chart.categoryAxis.labels.fontSize = 12
    chart.categoryAxis.labels.boxAnchor = "e"
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = 1
    chart.valueAxis.valueStep = 0.2
    chart.valueAxis.labels.fontName = FONT
    chart.valueAxis.labels.fontSize = 12
    chart.bars[0].fillColor = colors.HexColor("#2F75B5")
    chart.bars[1].fillColor = colors.HexColor("#ED7D31")
    chart.bars[2].fillColor = colors.HexColor("#70AD47")
    chart.barSpacing = 1.5
    chart.groupSpacing = 5
    drawing.add(chart)

    legend = Legend()
    legend.x = 150
    legend.y = 25
    legend.fontName = FONT
    legend.fontSize = 12
    legend.dx = 10
    legend.dy = 10
    legend.deltax = 95
    legend.deltay = 0
    legend.columnMaximum = 1
    legend.colorNamePairs = [
        (colors.HexColor("#2F75B5"), "Recall"),
        (colors.HexColor("#ED7D31"), "F1-score"),
        (colors.HexColor("#70AD47"), "ROC-AUC"),
    ]
    drawing.add(legend)
    drawing.hAlign = "CENTER"
    return drawing


def add_model_figure(story, number, title, csv_name):
    drawing = metric_chart(csv_name)
    block = [
        drawing,
        Paragraph(
            f"Figure {number}. {escape(title)}",
            STYLES["figure_caption"],
        ),
        Paragraph(
            "<i>Note.</i> Values show test-set recall, F1-score, and ROC-AUC for the at-risk class.",
            STYLES["figure_note"],
        ),
    ]
    story.append(KeepTogether(block))


def draw_cover(canvas, doc):
    canvas.saveState()
    width, height = letter
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(1.2)
    canvas.rect(0.45 * inch, 0.45 * inch, width - 0.9 * inch, height - 0.9 * inch)

    abu_logo = ASSETS_DIR / "abu_mark.png"
    engineering_logo = ASSETS_DIR / "computer_engineering_logo.png"
    if abu_logo.exists():
        canvas.drawImage(
            str(abu_logo),
            width / 2 - 0.45 * inch,
            height - 1.75 * inch,
            width=0.9 * inch,
            height=0.8 * inch,
            preserveAspectRatio=True,
            mask="auto",
        )
    if engineering_logo.exists():
        canvas.drawImage(
            str(engineering_logo),
            width - 1.95 * inch,
            0.6 * inch,
            width=1.25 * inch,
            height=1.05 * inch,
            preserveAspectRatio=True,
            mask="auto",
        )
    canvas.restoreState()


def page_number(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(colors.black)
    canvas.setFont(FONT, 12)
    canvas.drawCentredString(letter[0] / 2, 0.55 * inch, str(doc.page - 1))
    canvas.restoreState()


def add_cover(story):
    story.append(Spacer(1, 1.35 * inch))
    lines = [
        "SCHOOL OF POSTGRADUATE STUDIES",
        "AHMADU BELLO UNIVERSITY, ZARIA",
        "FACULTY OF ENGINEERING",
        "DEPARTMENT OF COMPUTER ENGINEERING",
        "",
        "MSc ARTIFICIAL INTELLIGENCE",
        "",
        "COURSE CODE:",
        COURSE_CODE,
        "",
        "COURSE TITLE:",
        COURSE_TITLE,
        "",
        "2025/2026 First Semester Project-Based Examination",
        "",
        "SUBMITTED BY:",
        NAME,
        f"Reg. No: {REG_NO}",
        "",
        "PROJECT TITLE",
        PROJECT_TITLE,
        "",
        "SUBMITTED TO:",
        LECTURER,
        "",
        "June, 2026",
    ]
    for line in lines:
        story.append(Paragraph(escape(line) if line else "&nbsp;", STYLES["cover"]))
    story.append(PageBreak())


def add_abstract(story):
    h1(story, "Abstract")
    story.append(
        para(
            "This project applies supervised machine learning to predict students who may be at risk of failing a final course grade. The study uses the public UCI Student Performance dataset, specifically the Portuguese language subset with 649 records (UCI Machine Learning Repository, n.d.). The target variable was engineered as At_Risk = 1 when the final grade G3 is below 10 out of 20. Two experimental settings were compared: an early-warning setting that excludes prior grades G1 and G2, and a performance-aware setting that includes them. Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, Support Vector Machine, and a Dummy Majority baseline were evaluated using reproducible preprocessing pipelines and cross-validation. The best early-warning model was Random Forest, achieving 0.800 recall and 0.582 F1-score for at-risk students. The best performance-aware model was Support Vector Machine, achieving 0.908 accuracy, 0.850 recall, 0.739 F1-score, and 0.936 ROC-AUC. The results show that machine learning can support early academic intervention, provided the system is used responsibly and evaluated beyond accuracy alone.",
            "body0",
        )
    )
    story.append(PageBreak())


def chapter_one(story):
    h1(story, "CHAPTER ONE")
    h2(story, "Introduction")
    story.append(
        para(
            "This report presents an end-to-end supervised machine learning project for predicting students who may be at risk of failing a course. The work responds to the COEN807 term project requirement by selecting a credible public dataset, defining a practical learning problem, building reproducible models, comparing algorithms, and interpreting the results for real educational decision support.",
            "body0",
        )
    )
    h2(story, "Background of the Study")
    story.append(
        para(
            "Machine learning is increasingly used in educational analytics because schools and universities need earlier evidence about students who may require academic support. A model that identifies risk before final results can help advisers, lecturers, and departments provide tutoring, counselling, or closer follow-up. However, such a model must be evaluated carefully because high accuracy alone can hide poor performance on the minority group of students who are actually at risk.",
        )
    )
    h2(story, "Problem Statement")
    story.append(
        para(
            "The problem addressed in this project is the prediction of whether a student will be at risk of failing based on available demographic, school, family, behavioural, and academic attributes. The original final grade is converted into a binary target, where At_Risk equals 1 if the final grade G3 is less than 10 out of 20 and 0 otherwise.",
        )
    )
    h2(story, "Aim and Objectives")
    story.append(
        para(
            "The aim of the study is to design and evaluate supervised classification models for predicting at-risk student academic performance. The specific objectives are stated below.",
        )
    )
    bullet(story, "To formulate the prediction task as a binary supervised learning problem.")
    bullet(story, "To justify the selected public dataset and describe its quality and limitations.")
    bullet(story, "To preprocess the data and engineer a clear At_Risk target variable.")
    bullet(story, "To compare several classification models using the same experimental protocol.")
    bullet(story, "To evaluate the models using recall, precision, F1-score, ROC-AUC, balanced accuracy, and confusion matrices.")
    bullet(story, "To discuss bias, ethical use, reproducibility, and practical deployment issues.")
    h2(story, "Scope and Significance")
    story.append(
        para(
            "The scope is limited to the UCI Student Performance dataset and a binary classification task. Two experimental settings are considered: an early-warning setting that excludes prior period grades G1 and G2, and a performance-aware setting that includes them. The significance of the work is that it demonstrates how machine learning can support educational intervention while also showing why careful metric selection and ethical safeguards are necessary.",
        )
    )


def chapter_two(story):
    h1(story, "CHAPTER TWO")
    h2(story, "Literature Review")
    story.append(
        para(
            "Supervised machine learning is concerned with learning a relationship between input features and known target labels. In classification problems, the target is categorical. For this study, the label indicates whether a student is at risk or not at risk. Educational prediction studies often use demographic information, attendance, study time, previous performance, and family background to estimate academic outcomes (Cortez & Silva, 2008).",
            "body0",
        )
    )
    h2(story, "Supervised Classification")
    story.append(
        para(
            "Classification algorithms learn decision boundaries that separate classes. Logistic Regression provides an interpretable linear baseline, Decision Tree models provide rule-based decisions, Random Forest and Gradient Boosting improve performance through ensembles of trees, and Support Vector Machine models search for a separating margin that can work well in high-dimensional feature spaces (Bishop, 2006; Goodfellow et al., 2016).",
        )
    )
    h2(story, "Evaluation of Imbalanced Data")
    story.append(
        para(
            "The selected target is imbalanced because far fewer students are labelled as at risk than not at risk. In such cases, accuracy can be misleading. A model may obtain high accuracy by predicting the majority class but still fail to identify students who need support. For this reason, recall and F1-score for the At_Risk class are treated as important evaluation measures.",
        )
    )
    h2(story, "Dataset Description and Justification")
    story.append(
        para(
            "The dataset was sourced from the UCI Machine Learning Repository. It contains student achievement records collected from two Portuguese secondary schools and was originally used for student performance prediction research (Cortez & Silva, 2008; UCI Machine Learning Repository, n.d.). The Portuguese language subset was selected because it contains 649 records, which is larger than the Mathematics subset and is suitable for a compact but meaningful supervised learning experiment.",
        )
    )
    add_table(
        story,
        ["Dataset property", "Value"],
        [
            ["Source", "UCI Student Performance dataset"],
            ["Selected file", "student-por.csv"],
            ["Records and variables", "649 students; 33 original variables"],
            ["Target variable", "At_Risk = 1 if G3 < 10, otherwise 0"],
            ["Class and quality", "100 at-risk; 549 not-at-risk; 0 missing values"],
        ],
        [2.1 * inch, 4.25 * inch],
        number=1,
        title="Summary of the Selected Dataset",
    )


def chapter_three(story):
    h1(story, "CHAPTER THREE")
    h2(story, "Methodology")
    story.append(
        para(
            "The study followed a reproducible machine learning workflow implemented with scikit-learn tools (Pedregosa et al., 2011). The raw student dataset was loaded, the At_Risk target was engineered from the final grade, preprocessing was applied through a pipeline, several models were trained, and the best models were selected using cross-validation on the training data.",
            "body0",
        )
    )
    h2(story, "Data Preprocessing")
    story.append(
        para(
            "Categorical features were encoded using one-hot encoding, while numerical features were imputed and standardised. Although the selected dataset had no missing values, imputation was included in the pipeline to make the workflow robust. The train-test split used 80% of the data for training and 20% for testing, with stratification to preserve the class ratio (Pedregosa et al., 2011).",
        )
    )
    h2(story, "Feature Engineering")
    story.append(
        para(
            "The final grade G3 was converted into the target variable At_Risk. A student was labelled as at risk when G3 was below 10. Two feature settings were designed. The early-warning experiment removed G1 and G2 so that the model used information available before later performance records. The performance-aware experiment included G1 and G2 to measure the improvement obtained when prior grades are available.",
        )
    )
    h2(story, "Methodology and Model Selection")
    add_table(
        story,
        ["Model", "Reason for inclusion"],
        [
            ["Dummy Majority", "Baseline for checking whether accuracy is misleading."],
            ["Logistic Regression", "Interpretable linear classifier."],
            ["Decision Tree", "Simple rule-based nonlinear model."],
            ["Random Forest", "Robust ensemble of decision trees."],
            ["Gradient Boosting", "Sequential ensemble that reduces errors iteratively."],
            ["Support Vector Machine", "Margin-based classifier for nonlinear separation."],
        ],
        [1.9 * inch, 4.45 * inch],
        number=2,
        title="Classification Models Selected for Comparison",
    )
    h2(story, "Experimental Design")
    story.append(
        para(
            "Each model was trained under the two feature settings. Hyperparameters were tuned using five-fold stratified cross-validation on the training data only. The tuning score was F1-score for the At_Risk class because the project aims to detect vulnerable students while still controlling false alarms. Final results were computed once on the untouched test set, using accuracy, balanced accuracy, precision, recall, F1-score, ROC-AUC, and confusion matrix counts.",
        )
    )


def chapter_four(story):
    h1(story, "CHAPTER FOUR")
    h2(story, "Results and Evaluation")
    story.append(
        para(
            "The two experiments produced different practical insights. The early-warning experiment is harder because it excludes prior grades, but it is useful when intervention must begin before later academic records are available. The performance-aware experiment is more predictive because it includes G1 and G2, but it may identify risk later.",
            "body0",
        )
    )
    h2(story, "Early-Warning Experiment Without G1 and G2")
    story.append(
        para(
            "In the early-warning setting, the Random Forest model produced the best At_Risk F1-score. It achieved 0.800 recall and 0.582 F1-score for at-risk students, meaning it identified 16 out of 20 at-risk students in the test set. The Dummy Majority baseline achieved high accuracy but detected no at-risk students, confirming that accuracy alone is not sufficient.",
        )
    )
    add_table(
        story,
        ["Model", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC"],
        metric_rows("metrics_early_warning_without_prior_grades.csv"),
        [1.75 * inch, 0.85 * inch, 0.85 * inch, 0.85 * inch, 0.75 * inch, 0.9 * inch],
        number=3,
        title="Early-Warning Experiment Results Without G1 and G2",
        numeric_columns=True,
    )
    add_model_figure(
        story,
        1,
        "Early-Warning Model Comparison",
        "metrics_early_warning_without_prior_grades.csv",
    )
    h2(story, "Performance-Aware Experiment With G1 and G2")
    story.append(
        para(
            "When G1 and G2 were included, overall predictive performance improved. The Support Vector Machine achieved the best At_Risk F1-score, with 0.908 accuracy, 0.850 recall, 0.739 F1-score, and 0.936 ROC-AUC. This shows that prior grades are strong predictors of final academic risk.",
        )
    )
    add_table(
        story,
        ["Model", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC"],
        metric_rows("metrics_performance_aware_with_prior_grades.csv"),
        [1.75 * inch, 0.85 * inch, 0.85 * inch, 0.85 * inch, 0.75 * inch, 0.9 * inch],
        number=4,
        title="Performance-Aware Experiment Results With G1 and G2",
        numeric_columns=True,
    )
    add_model_figure(
        story,
        2,
        "Performance-Aware Model Comparison",
        "metrics_performance_aware_with_prior_grades.csv",
    )
    h2(story, "Comparative Analysis and Discussion")
    story.append(
        para(
            "The main finding is that the best model depends on the intended use. If the aim is early intervention, the Random Forest early-warning model is useful because it does not depend on prior grades. If the aim is more accurate prediction after some academic records exist, the Support Vector Machine model is stronger. In both cases, the model should support human academic advising rather than replace it.",
        )
    )
    h2(story, "Limitations, Biases, and Lessons Learned")
    story.append(
        para(
            "The dataset contains variables such as address type, parental education, internet access, family support, and school support. These variables may reflect socioeconomic differences. Therefore, the model should guide support, not punishment or exclusion.",
        )
    )


def chapter_five(story):
    h1(story, "CHAPTER FIVE")
    h2(story, "Conclusion and Future Work")
    story.append(
        para(
            "This project demonstrates a complete supervised machine learning workflow for predicting at-risk student performance using a credible public dataset. The work covered problem formulation, dataset justification, preprocessing, model design, experimental comparison, evaluation, interpretation, ethical discussion, and reproducibility documentation.",
            "body0",
        )
    )
    h2(story, "Conclusion")
    story.append(
        para(
            "The early-warning Random Forest model detected 80% of at-risk students without using prior grade variables, while the performance-aware Support Vector Machine achieved stronger overall performance after including G1 and G2. The results show that machine learning can support academic intervention, but the model must be evaluated using minority-class metrics and interpreted with caution.",
        )
    )
    h2(story, "Future Work")
    bullet(story, "Externally validate the models on an independent, multi-institution Nigerian student dataset.")
    bullet(story, "Use nested stratified cross-validation and bootstrap confidence intervals for model comparison.")
    bullet(story, "Optimize decision thresholds with cost-sensitive analysis and assess calibration using Brier score and reliability curves.")
    bullet(story, "Evaluate robustness, SHAP or permutation importance, subgroup fairness metrics, and additional ensemble models such as XGBoost.")
    h2(story, "Reproducibility and Repository")
    story.append(
        para(
            "The project repository contains the source code, dataset/access instructions, processed data, trained models, result tables, visualizations, final report, presentation slides, requirements file, and reproduction instructions. The GitHub repository link is: "
            + GITHUB_URL,
        )
    )
    story.append(PageBreak())
    h1(story, "REFERENCES")
    references = [
        "Cortez, P., & Silva, A. (2008). Using data mining to predict secondary school student performance. Proceedings of the 5th FUture BUsiness TEChnology Conference.",
        "UCI Machine Learning Repository. (n.d.). Student Performance dataset. https://archive.ics.uci.edu/dataset/320/student+performance",
        "Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. Journal of Machine Learning Research, 12, 2825-2830.",
        "Bishop, C. M. (2006). Pattern recognition and machine learning. Springer.",
        "Goodfellow, I., Bengio, Y., & Courville, A. (2016). Deep learning. MIT Press.",
    ]
    for ref in references:
        story.append(para(ref, "ref"))


def build():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    story = []
    add_cover(story)
    add_abstract(story)
    chapter_one(story)
    chapter_two(story)
    chapter_three(story)
    chapter_four(story)
    chapter_five(story)

    doc = SimpleDocTemplate(
        str(REPORT_PATH),
        pagesize=letter,
        leftMargin=1.0 * inch,
        rightMargin=1.0 * inch,
        topMargin=1.0 * inch,
        bottomMargin=1.0 * inch,
    )
    doc.build(story, onFirstPage=draw_cover, onLaterPages=page_number)
    print(REPORT_PATH)


if __name__ == "__main__":
    build()
