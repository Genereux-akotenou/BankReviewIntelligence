import re
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# UTILS
# -------------------------------------------------------------------
def parse_relative_date(relative_date_str):
        match = re.search(r"il y a (\d+) (\w+)", relative_date_str)
        if not match:
            return None
        quantity = int(match.group(1))
        unit = match.group(2)
        if unit in ['ans', 'an']:
            return datetime.now() - timedelta(days=quantity * 365)
        elif unit == 'mois':
            return datetime.now() - timedelta(days=quantity * 30)
        elif unit in ['semaines', 'semaine']:
            return datetime.now() - timedelta(weeks=quantity)
        elif unit in ['jours', 'jour']:
            return datetime.now() - timedelta(days=quantity)
        elif unit in ['heures', 'heure']:
            return datetime.now() - timedelta(hours=quantity)
        elif unit in ['minutes', 'minute']:
            return datetime.now() - timedelta(minutes=quantity)
        else:
            return None
    
# CORE
# -------------------------------------------------------------------
def preprocess_dataframe(df):
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
    
    
    # Function to extract topics using LDA
    def extract_topics(text_series, n_topics=2):
        vectorizer = CountVectorizer(stop_words='french')
        X = vectorizer.fit_transform(text_series)
        lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
        lda.fit(X)
        topics = lda.transform(X)
        return topics

    # Extract good and bad topics from Reviewer_Text
    text_topics = extract_topics(df['Reviewer_Text'])
    df['Good_Topic'] = text_topics[:, 0]
    df['Bad_Topic'] = text_topics[:, 1]

    

    return df

# TEST
# -------------------------------------------------------------------
# df = pd.read_parquet('path_to_parquet_file')
# processed_df = preprocess_dataframe(df)
# processed_df.to_parquet('path_to_processed_parquet_file', index=False)
