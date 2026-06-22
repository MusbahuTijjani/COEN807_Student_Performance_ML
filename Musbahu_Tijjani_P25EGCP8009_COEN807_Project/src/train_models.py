from pathlib import Path
import json
import pickle
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOCAL_DEPS = PROJECT_ROOT / "deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    RocCurveDisplay,
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier


RANDOM_STATE = 42
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "student" / "student-por.csv"
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = PROJECT_ROOT / "figures"
MODELS_DIR = PROJECT_ROOT / "models"


def ensure_dirs():
    for directory in [RESULTS_DIR, FIGURES_DIR, MODELS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def load_dataset():
    df = pd.read_csv(DATA_PATH, sep=";")
    df["At_Risk"] = (df["G3"] < 10).astype(int)
    return df


def build_preprocessor(x_train):
    numeric_cols = x_train.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_cols = x_train.select_dtypes(exclude=["int64", "float64"]).columns.tolist()

    numeric_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, numeric_cols),
            ("cat", categorical_pipe, categorical_cols),
        ]
    )
    return preprocessor


def candidate_models():
    return {
        "Dummy_Majority": (
            DummyClassifier(strategy="most_frequent"),
            {},
        ),
        "Logistic_Regression": (
            LogisticRegression(max_iter=3000, class_weight="balanced", random_state=RANDOM_STATE),
            {
                "model__C": [0.1, 1.0, 10.0],
                "model__solver": ["liblinear"],
            },
        ),
        "Decision_Tree": (
            DecisionTreeClassifier(class_weight="balanced", random_state=RANDOM_STATE),
            {
                "model__max_depth": [3, 5, 8, None],
                "model__min_samples_leaf": [1, 5, 10],
            },
        ),
        "Random_Forest": (
            RandomForestClassifier(class_weight="balanced", random_state=RANDOM_STATE, n_jobs=1),
            {
                "model__n_estimators": [150, 300],
                "model__max_depth": [5, 10, None],
                "model__min_samples_leaf": [1, 5],
            },
        ),
        "Gradient_Boosting": (
            GradientBoostingClassifier(random_state=RANDOM_STATE),
            {
                "model__n_estimators": [100, 200],
                "model__learning_rate": [0.03, 0.1],
                "model__max_depth": [2, 3],
            },
        ),
        "Support_Vector_Machine": (
            SVC(class_weight="balanced", random_state=RANDOM_STATE),
            {
                "model__C": [0.5, 1.0, 3.0],
                "model__kernel": ["rbf", "linear"],
            },
        ),
    }


def get_scores(estimator, x_test):
    if hasattr(estimator, "predict_proba"):
        return estimator.predict_proba(x_test)[:, 1]
    if hasattr(estimator, "decision_function"):
        return estimator.decision_function(x_test)
    return estimator.predict(x_test)


def evaluate_model(name, estimator, x_test, y_test, experiment):
    y_pred = estimator.predict(x_test)
    y_score = get_scores(estimator, x_test)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred, labels=[0, 1]).ravel()

    try:
        auc = roc_auc_score(y_test, y_score)
    except ValueError:
        auc = np.nan

    return {
        "experiment": experiment,
        "model": name,
        "accuracy": accuracy_score(y_test, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y_test, y_pred),
        "precision_at_risk": precision_score(y_test, y_pred, zero_division=0),
        "recall_at_risk": recall_score(y_test, y_pred, zero_division=0),
        "f1_at_risk": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": auc,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def plot_class_distribution(df):
    counts = df["At_Risk"].value_counts().sort_index()
    labels = ["Not at risk", "At risk"]
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, counts.values, color=["#2E6F9E", "#B23A48"])
    ax.set_title("Target Class Distribution")
    ax.set_ylabel("Number of students")
    for bar, value in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 5, str(value), ha="center")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "class_distribution.png", dpi=180)
    plt.close(fig)


def plot_metric_comparison(metrics_df):
    order = metrics_df.sort_values("f1_at_risk", ascending=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(order))
    width = 0.26
    ax.bar(x - width, order["recall_at_risk"], width, label="Recall")
    ax.bar(x, order["f1_at_risk"], width, label="F1")
    ax.bar(x + width, order["roc_auc"], width, label="ROC-AUC")
    ax.set_xticks(x)
    ax.set_xticklabels(order["model"], rotation=35, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_title("Model Comparison for At-Risk Student Detection")
    ax.set_ylabel("Score")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / f"model_comparison_{order['experiment'].iloc[0]}.png", dpi=180)
    plt.close(fig)


def plot_confusion_matrix(best_name, best_model, x_test, y_test, experiment):
    fig, ax = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay.from_estimator(
        best_model,
        x_test,
        y_test,
        display_labels=["Not at risk", "At risk"],
        cmap="Blues",
        ax=ax,
        colorbar=False,
    )
    ax.set_title(f"Confusion Matrix: {best_name}")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / f"confusion_matrix_{experiment}.png", dpi=180)
    plt.close(fig)


def plot_roc_curves(fitted_models, x_test, y_test, experiment):
    fig, ax = plt.subplots(figsize=(6, 5))
    for name, model in fitted_models.items():
        if name == "Dummy_Majority":
            continue
        RocCurveDisplay.from_estimator(model, x_test, y_test, ax=ax, name=name.replace("_", " "))
    ax.set_title(f"ROC Curves: {experiment.replace('_', ' ').title()}")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / f"roc_curves_{experiment}.png", dpi=180)
    plt.close(fig)


def run_experiment(df, experiment, include_prior_grades):
    drop_cols = ["G3", "At_Risk"]
    if not include_prior_grades:
        drop_cols.extend(["G1", "G2"])

    x = df.drop(columns=drop_cols)
    y = df["At_Risk"]

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )

    preprocessor = build_preprocessor(x_train)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    rows = []
    fitted = {}
    best_params = {}

    for name, (model, grid) in candidate_models().items():
        pipe = Pipeline(steps=[("preprocess", preprocessor), ("model", model)])
        if grid:
            search = GridSearchCV(
                pipe,
                grid,
                cv=cv,
                scoring="f1",
                n_jobs=1,
                refit=True,
            )
            search.fit(x_train, y_train)
            fitted_model = search.best_estimator_
            best_params[name] = search.best_params_
        else:
            fitted_model = pipe.fit(x_train, y_train)
            best_params[name] = {}

        fitted[name] = fitted_model
        rows.append(evaluate_model(name, fitted_model, x_test, y_test, experiment))

    metrics = pd.DataFrame(rows).sort_values("f1_at_risk", ascending=False)
    metrics.to_csv(RESULTS_DIR / f"metrics_{experiment}.csv", index=False)

    best_row = metrics.iloc[0]
    best_name = best_row["model"]
    best_model = fitted[best_name]
    with open(MODELS_DIR / f"best_model_{experiment}.pkl", "wb") as f:
        pickle.dump(best_model, f)

    plot_metric_comparison(metrics)
    plot_confusion_matrix(best_name, best_model, x_test, y_test, experiment)
    plot_roc_curves(fitted, x_test, y_test, experiment)

    summary = {
        "experiment": experiment,
        "include_prior_grades": include_prior_grades,
        "train_size": int(len(x_train)),
        "test_size": int(len(x_test)),
        "feature_count_before_encoding": int(x.shape[1]),
        "positive_class": "At_Risk = 1 when G3 < 10",
        "best_model": best_name,
        "best_metrics": best_row.to_dict(),
        "best_params": best_params,
    }
    with open(RESULTS_DIR / f"summary_{experiment}.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    return metrics, summary


def main():
    ensure_dirs()
    df = load_dataset()

    dataset_summary = {
        "source": "UCI Machine Learning Repository - Student Performance dataset",
        "records": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "target": "At_Risk = 1 if G3 < 10 else 0",
        "at_risk_count": int(df["At_Risk"].sum()),
        "not_at_risk_count": int((df["At_Risk"] == 0).sum()),
        "at_risk_rate": float(df["At_Risk"].mean()),
        "missing_values": int(df.isna().sum().sum()),
    }
    with open(RESULTS_DIR / "dataset_summary.json", "w", encoding="utf-8") as f:
        json.dump(dataset_summary, f, indent=2)
    df.to_csv(PROJECT_ROOT / "data" / "student_performance_portuguese_with_target.csv", index=False)
    plot_class_distribution(df)

    early_metrics, early_summary = run_experiment(
        df, experiment="early_warning_without_prior_grades", include_prior_grades=False
    )
    extended_metrics, extended_summary = run_experiment(
        df, experiment="performance_aware_with_prior_grades", include_prior_grades=True
    )

    combined = pd.concat([early_metrics, extended_metrics], ignore_index=True)
    combined.to_csv(RESULTS_DIR / "all_model_metrics.csv", index=False)

    print("COEN807 Student Performance ML project completed.")
    print("Dataset records:", dataset_summary["records"])
    print("At-risk rate:", round(dataset_summary["at_risk_rate"], 3))
    print("Best early-warning model:", early_summary["best_model"])
    print("Best performance-aware model:", extended_summary["best_model"])
    print("Results saved to:", RESULTS_DIR)


if __name__ == "__main__":
    main()
