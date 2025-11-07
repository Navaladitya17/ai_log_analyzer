import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from joblib import dump
import os

# ---------- UTILITIES ----------

def optimize_df_for_memory(df):
    """Downcast numeric columns to reduce memory usage."""
    df = df.copy()
    for c in df.select_dtypes(include=["int64"]).columns:
        df[c] = pd.to_numeric(df[c], downcast="unsigned")
    for c in df.select_dtypes(include=["float64"]).columns:
        df[c] = pd.to_numeric(df[c], downcast="float")
    return df


def make_numeric_view(df):
    """Convert non-numeric columns to categorical codes for ML."""
    tmp = df.copy()
    for col in tmp.select_dtypes(include=["object", "category"]).columns:
        tmp[col] = pd.Categorical(tmp[col]).codes
    tmp = tmp.fillna(0)
    numeric = tmp.select_dtypes(include=[np.number])
    return numeric


# ---------- DETECT (for small/medium CSV) ----------

def detect(df, contamination=0.05, max_samples=10000):
    """
    Detect anomalies in-memory using Isolation Forest.
    Returns:
        df_all -> full dataframe with Anomaly column
        anomalies -> subset of anomalies only
    """
    if df is None or df.empty:
        return pd.DataFrame(), pd.DataFrame()

    df_display = df.copy().reset_index(drop=True)
    df_mem = optimize_df_for_memory(df_display)

    X = make_numeric_view(df_mem)
    if X.shape[1] == 0:
        df_display["Anomaly"] = 1
        return df_display, pd.DataFrame(columns=df_display.columns)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        contamination=contamination,
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        max_samples=min(max_samples, len(X_scaled))
    )
    preds = model.fit_predict(X_scaled)

    df_display["Anomaly"] = preds
    anomalies = df_display[df_display["Anomaly"] == -1].copy().reset_index(drop=True)

    try:
        dump(model, "ai_log_model.joblib")
    except Exception:
        pass

    return df_display, anomalies


# ---------- DETECT LARGE (chunked for big CSV) ----------

def detect_large(path, contamination=0.05, sample_rows=100000, chunksize=200000):
    """
    Chunked anomaly detection for large CSV files.
    """
    reader = pd.read_csv(path, chunksize=chunksize, low_memory=False)
    try:
        first_chunk = next(reader)
    except StopIteration:
        return pd.DataFrame()

    first_chunk_display = first_chunk.copy().reset_index(drop=True)
    first_chunk_mem = optimize_df_for_memory(first_chunk_display)
    numeric_view = make_numeric_view(first_chunk_mem)
    numeric_cols = numeric_view.columns.tolist()

    if not numeric_cols:
        return pd.DataFrame(columns=first_chunk.columns)

    sample = numeric_view.sample(min(len(numeric_view), sample_rows), random_state=42)
    scaler = StandardScaler()
    Xs = scaler.fit_transform(sample[numeric_cols])

    model = IsolationForest(
        contamination=contamination,
        n_estimators=200,
        random_state=42,
        max_samples=min(10000, len(Xs))
    )
    model.fit(Xs)

    anomalies_parts = []
    for chunk in pd.read_csv(path, chunksize=chunksize, low_memory=False):
        chunk_display = chunk.copy().reset_index(drop=True)
        chunk_numeric = make_numeric_view(chunk)

        # ensure consistent numeric columns
        for col in numeric_cols:
            if col not in chunk_numeric:
                chunk_numeric[col] = 0

        preds = model.predict(chunk_numeric[numeric_cols])
        chunk_display["Anomaly"] = preds
        chunk_anomalies = chunk_display[chunk_display["Anomaly"] == -1].copy()
        if not chunk_anomalies.empty:
            anomalies_parts.append(chunk_anomalies)

    return pd.concat(anomalies_parts, ignore_index=True) if anomalies_parts else pd.DataFrame(columns=first_chunk.columns)
