import requests
import pandas as pd
import time

class TopicExtractor:
    def __init__(self, model="llama3", patience=3, url='http://localhost:11434/api/generate'):
        self.url = url
        self.model = model
        self.max_try = patience
        self.topics = [
            "service_client",
            "produits_financiers",
            "expérience_utilisateur",
            "gestion_des_comptes",
            "sécurité",
            "localisation_accessibilité",
            "services_additionnels"
        ]
        self.format1 = """
        {topics: [
            ('topic1', 'Positive', ['sous topic', 'sous topic', ...]),
            ('topic2', 'Negative', ['sous topic', 'sous topic', ...]),
            ('topic3', 'Neutral', ['sous topic', 'sous topic', ...]),
        ]}
        NB: un 'topic' ou 'sous topic' est un groupe de mot ou un mot.
        Donne juste la sortie JSON. Pas de commentaire supplementaire.   
        Voici une exemple de sortie:
        {
            "topics": [
              ("ouverture de compte", "Positive", ["rapide", "simple"]),
              ("Service client", "Negative", ["arrogant", "lent"]),
              ("Recommandation", "Neutre", []),
            ]
        }
       Si le review est NAN, Sortie: {'topics': []}. Pour le review donne la sortie conrespondant a son analyse """
        #Utilise seulement ces topics . Pas d'autres. """ + str(self.topics)

    def _send_request(self, prompt):
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(self.url, json=data)
        if response.status_code == 200:
            response_data = response.json()
            #print(response_data['response'])
            return response_data.get('response', 'No response field found')
        else:
            raise Exception(f"Failed to retrieve data, status code {response.status_code}")
    
    def extract(self, reviews, type='SINGLE_SOURCE'):
        #print("REVIEW: ", reviews)
        if reviews == "NAN":
            return {'topics': []}
        else:
            tries = 0
            while tries < self.max_try:
                try:
                    if type == 'SINGLE_SOURCE':
                        if isinstance(reviews, str):
                            prompt = f"Extraire les topics de cette revue '{reviews}'. et donne la sortie au **format JSON** suiavnt: " + self.format1
                            response = self._send_request(prompt)
                            return self._parse_single_response(response)
                        else:
                            raise AssertionError("For SINGLE_SOURCE, reviews should be a single string.")
                    else:
                        raise AssertionError("type arg should either be 'SINGLE_SOURCE' or 'MULTI_SOURCE'")
                except Exception as e:
                    print(f"Attempt {tries + 1} failed with error: {e}")
                    tries += 1
                    time.sleep(2)
            return f"Failed to extract topics after {self.max_try} attempts"
        
    @staticmethod
    def _safejson(response):
        first_brace = response.find('{')
        last_brace = response.rfind('}')
        if last_brace == -1:
            response += "}"
        last_brace = response.rfind('}')
        if first_brace == -1 or last_brace == -1:
            raise ValueError("No JSON object could be identified in the response")
        return response[first_brace:last_brace + 1]
        
    def _parse_single_response(self, response):
        try:
            response = self._safejson(response)
            parsed_response = eval(response)
            formatted_response = {
                "topics": parsed_response.get("topics", []),
            }
            return formatted_response
        except Exception as e:
            raise Exception(f"Failed to parse response: {e}")

    @staticmethod
    def _flatten_topics(topics):
        flat_data = []
        for topic in topics.get('topics', []):
            flat_data.append({
                "topic": topic[0],
                "sentiment": topic[1],
                "subtopics": topic[2]
            })
        return flat_data
    
    def to_dataframe(self, topics):
        flat_data = self._flatten_topics(topics)
        return pd.DataFrame(flat_data)