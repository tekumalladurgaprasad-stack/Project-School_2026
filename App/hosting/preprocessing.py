
import pandas as pd

NUMERIC_FEATURES = [
    "LIMIT_BAL", "AGE",
    "PAY_1", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
    "BILL_AMT1", "BILL_AMT2", "BILL_AMT3",
    "BILL_AMT4", "BILL_AMT5", "BILL_AMT6",
    "PAY_AMT1", "PAY_AMT2", "PAY_AMT3",
    "PAY_AMT4", "PAY_AMT5", "PAY_AMT6"
]

REQUIRED_INPUTS = set(
    NUMERIC_FEATURES
    + ["SEX", "EDUCATION", "MARRIAGE"]
)

def preprocess(raw_features, features):

    data = dict(raw_features)

    data.pop("ID", None)
    data.pop("DEFAULT", None)

    if "PAY_0" in data:
        data["PAY_1"] = data.pop("PAY_0")

    missing = REQUIRED_INPUTS - data.keys()

    if missing:
        raise ValueError(f"Missing features: {sorted(missing)}")

    education = int(data["EDUCATION"])
    marriage = int(data["MARRIAGE"])
    sex = int(data["SEX"])

    if education in (0, 6):
        education = 5

    if education not in (1, 2, 3, 4, 5):
        raise ValueError("Invalid education category")

    if marriage not in (0, 1, 2, 3):
        raise ValueError("Invalid marriage category")

    if sex not in (1, 2):
        raise ValueError("Invalid sex category")

    row = {
        feature: float(data[feature])
        for feature in NUMERIC_FEATURES
    }

    row["SEX"] = 0 if sex == 1 else 1

    for category in (2, 3, 4, 5):
        row[f"EDUCATION_{category}"] = int(
            education == category
        )

    for category in (1, 2, 3):
        row[f"MARRIAGE_{category}"] = int(
            marriage == category
        )

    result = pd.DataFrame([row])

    return result.reindex(columns=features)
