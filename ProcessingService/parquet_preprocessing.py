import re
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# UTILS
# -------------------------------------------------------------------
def parse_relative_date(relative_date_str):
    #print(f"Processing: -{relative_date_str}-")
    if not relative_date_str or not isinstance(relative_date_str, str):
        return "0000-00-00"
    
    # Refined regex pattern to capture both words and numbers
    match = re.search(r"il y a (\d+|un|une) (\w+)", relative_date_str)
    if not match:
        print(f"No match for: {relative_date_str}")
        return "0000-00-00"
    
    # Convert 'un' or 'une' to 1
    quantity_str = match.group(1)
    if quantity_str in ["un", "une"]:
        quantity = 1
    else:
        quantity = int(quantity_str)
    
    unit = match.group(2).lower()
    now = datetime.now()
    
    if unit in ['ans', 'an']:
        return (now - timedelta(days=quantity * 365)).strftime('%Y-%m-%d')
    elif unit == 'mois':
        return (now - timedelta(days=quantity * 30)).strftime('%Y-%m-%d')
    elif unit in ['semaines', 'semaine']:
        return (now - timedelta(weeks=quantity)).strftime('%Y-%m-%d')
    elif unit in ['jours', 'jour']:
        return (now - timedelta(days=quantity)).strftime('%Y-%m-%d')
    elif unit in ['heures', 'heure']:
        return (now - timedelta(hours=quantity)).strftime('%Y-%m-%d')
    elif unit in ['minutes', 'minute']:
        return (now - timedelta(minutes=quantity)).strftime('%Y-%m-%d')
    else:
        print(f"Unrecognized unit: {unit}")
        return "0000-00-00"
    
# CORE
# -------------------------------------------------------------------
def preprocess_dataframe(df_init):
    df = df_init.copy()
    TRANSFORMATIONS = {
        'Country': lambda x: x.strip().title(),
        'Town': lambda x: x.strip().title(),
        'Bank_Name': lambda x: x.strip().title(),
        'Bank_Phone_number': lambda x: x.strip(),
        'Bank_Address': lambda x: x.strip().title(),
        'Bank_Website': lambda x: x.strip().lower(),
        'Reviewer_Nane': lambda x: x.strip().title(),
        'Reviewer_Sart': lambda x: int(x),
        'Reviewer_Text': lambda x: x.strip(),
        'Reviewer_Publish_Date': lambda x: parse_relative_date(x),
        'Reviewer_Like_Reaction': lambda x: int(x),
        'Reviewer_Profil_Link': lambda x: x.strip(),
        'Reviewer_Owner_Reply': lambda x: str(x).strip(),
        'Reviewer_Owner_Reply_Date': lambda x: parse_relative_date(x) if pd.notnull(x) or x!="NAN" else None
    }

    # Apply transformations to the dataframe
    for column, transformation in TRANSFORMATIONS.items():
        df[column] = df[column].apply(transformation)
    df['Topic'] = {}
    df['Sentiment'] = {}
    df['Sub_Topic'] = {}
    
    # Function to extract topics using LDA
    """def extract_topics(text_series, n_topics=2):
        vectorizer = CountVectorizer(stop_words='french')
        X = vectorizer.fit_transform(text_series)
        lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
        lda.fit(X)
        topics = lda.transform(X)
        return topics

    # Extract good and bad topics from Reviewer_Text
    text_topics = extract_topics(df['Reviewer_Text'])
    df['Good_Topic'] = text_topics[:, 0]
    df['Bad_Topic'] = text_topics[:, 1]"""

    return df

# TEST
# -------------------------------------------------------------------
# df = pd.read_parquet('path_to_parquet_file')
# processed_df = preprocess_dataframe(df)
# processed_df.to_parquet('path_to_processed_parquet_file', index=False)
