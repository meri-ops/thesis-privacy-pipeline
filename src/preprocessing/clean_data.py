"""Fase preprocessing: encoding delle feature per il training del modello.

Il synthesizer (Fase 2) e le metriche SDMetrics (Fase 3) lavorano bene con
colonne categoriche "raw" (stringhe), ma scikit-learn no: RandomForest e
LogisticRegression richiedono input numerico. Questo modulo prepara feature
e target per il training (Fase 4), separatamente per ogni esperimento:
il preprocessor va sempre fit SOLO sul training set di quello specifico
esperimento (reale o sintetico) e poi riusato, invariato, sul test set reale.
"""
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
import pandas as pd


def split_features_target(df: pd.DataFrame, target_column: str):
    """Separa un DataFrame in feature (X) e target (y)."""
    X = df.drop(columns=[target_column])
    y = df[target_column]
    return X, y


def build_preprocessor(numeric_columns: list, categorical_columns: list) -> ColumnTransformer:
    """Crea un ColumnTransformer non ancora addestrato: passthrough per le
    colonne numeriche, one-hot encoding per le categoriche.

    handle_unknown="ignore" e' importante quando il preprocessor e'
    addestrato sul sintetico (Esperimento B): eventuali categorie rare
    presenti nel test set reale ma non generate dal synthesizer non devono
    far fallire la transform, vengono semplicemente codificate come vettore
    di zeri.
    """
    return ColumnTransformer(
        transformers=[
            ("num", "passthrough", numeric_columns),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_columns),
        ]
    )


def encode_target(y_train: pd.Series, *y_others: pd.Series):
    """Addestra un LabelEncoder sul target di training e lo applica a
    y_train piu' a un numero arbitrario di altre serie (es. y_test,
    y_train_synthetic), cosi' tutte usano la STESSA mappatura classe->intero.
    Indispensabile per confrontare in modo coerente Esperimento A e B.

    Returns:
        (y_train_encoded, [y_other_encoded, ...], label_encoder)
    """
    encoder = LabelEncoder()
    y_train_enc = encoder.fit_transform(y_train)
    others_enc = [encoder.transform(y) for y in y_others]
    return y_train_enc, others_enc, encoder