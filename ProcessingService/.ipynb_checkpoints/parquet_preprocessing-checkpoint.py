import re
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# UTILS
# -------------------------------------------------------------------
def parse_relative_date(relative_date_str):
    if not relative_date_str or not isinstance(relative_date_str, str):
        return "0000-00-00"
    
    # Refined regex pattern to capture both words and numbers
    match = re.search(r"il y a (\d+|un|une) (\w+)", relative_date_str)
    if not match:
        #print(f"No match for: {relative_date_str}")
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
        'Country': lambda x: x.strip().title() if isinstance(x, str) else x,
        'Town': lambda x: x.strip().title() if isinstance(x, str) else x,
        'Bank_Name': lambda x: x.strip().title() if isinstance(x, str) else x,
        'Bank_Phone_number': lambda x: x.strip() if isinstance(x, str) else x,
        'Bank_Address': lambda x: x.strip().title() if isinstance(x, str) else x,
        'Bank_Website': lambda x: x.strip().lower() if isinstance(x, str) else x,
        'Reviewer_Nane': lambda x: x.strip().title() if isinstance(x, str) else x,
        'Reviewer_Sart': lambda x: int(x) if pd.notnull(x) else x,
        'Reviewer_Text': lambda x: x.strip() if isinstance(x, str) else x,
        'Reviewer_Publish_Date': lambda x: parse_relative_date(x) if pd.notnull(x) else "0000-00-00",
        'Reviewer_Like_Reaction': lambda x: int(x) if pd.notnull(x) else 0,
        'Reviewer_Profil_Link': lambda x: x.strip() if isinstance(x, str) else x,
        'Reviewer_Owner_Reply': lambda x: str(x).strip() if isinstance(x, str) else x,
        'Reviewer_Owner_Reply_Date': lambda x: parse_relative_date(x) if pd.notnull(x) and x != "NAN" else "0000-00-00"
    }

    # Apply transformations to the dataframe
    for column, transformation in TRANSFORMATIONS.items():
        if column in df.columns:
            df[column] = df[column].apply(transformation)
    
    df['Topic'] = {}
    df['Sentiment'] = {}
    df['Sub_Topic'] = {}
    return df

# Example usage
if __name__ == "__main__":
    all_data = pd.read_parquet('concatenated_data.parquet').sample(10)
    df = preprocess_dataframe(all_data)
    print(df.head())  # To check if the dataframe is processed correctly