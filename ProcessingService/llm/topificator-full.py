import requests
import pandas as pd
import time

class TopicExtractor:
    def __init__(self, model="llama3", max_try=3, url='http://localhost:11434/api/generate'):
        self.url = url
        self.model = model
        self.max_try = max_try
        self.format1 = "{ \
            primary_topic: [('topic1', 'Positive'), ('topic2', 'Negative'), ('topic3', 'Neutral'), (..., ...)], \
            detailed_topic: {'topic1':['subtopic', 'subtopic', ...], 'topic2': ['subtopic', ...]} \
        } .Give just json Output. No extra comment."
        self.format2 = "{ \
            'sentence1': {primary_topic: [('topic1', 'Positive'), ('topic2', 'Negative'), ('topic3', 'Neutral'), (..., ...)], \
                detailed_topic: {'topic1':['subtopic11', 'subtopic12', ...], 'topic2': ['subtopic21', ...]} }, \
            'sentence2': {primary_topic: [('topic1', 'Positive'), ('topic2', 'Negative'), ('topic3', 'Neutral'), (..., ...)], \
                detailed_topic: {'topic1':['subtopic11', 'subtopic12', ...], 'topic2': ['subtopic21', ...]} }, \
            'sentence3': ... \
        } .Give just json Output. No extra comment."

    def _send_request(self, prompt):
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(self.url, json=data)
        if response.status_code == 200:
            response_data = response.json()
            print(response_data['response'])
            return response_data.get('response', 'No response field found')
        else:
            raise Exception(f"Failed to retrieve data, status code {response.status_code}")
    
    def extract(self, reviews, type='SINGLE_SOURCE'):
        tries = 0
        while tries < self.max_try:
            try:
                if type == 'SINGLE_SOURCE':
                    if isinstance(reviews, str):
                        prompt = f"Extract topic from this review '{reviews}'. And output in this **JSON format**: " + self.format1
                        response = self._send_request(prompt)
                        return self._parse_single_response(response)
                    else:
                        raise AssertionError("For SINGLE_SOURCE, reviews should be a single string.")
                #elif type == 'MULTI_SOURCE':
                #    if isinstance(reviews, list):
                #        combined_reviews = " -- ".join(reviews)
                #        prompt = f"Extract topics from these reviews '{combined_reviews}'. And output in this **JSON format**: " + self.format2
                #        response = self._send_request(prompt)
                #        return self._parse_array_response(response)
                #    else:
                #        raise AssertionError("For MULTI_SOURCE, reviews should be a list of strings.")
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
        if first_brace == -1 or last_brace == -1:
            raise ValueError("No JSON object could be identified in the response")
        return response[first_brace:last_brace + 1]
        
    def _parse_single_response(self, response):
        try:
            response = self._safejson(response)
            parsed_response = eval(response)
            formatted_response = {
                "primary_topic": parsed_response.get("primary_topic", []),
                "detailed_topic": parsed_response.get("detailed_topic", {}),
                "sentiment": parsed_response.get("sentiment", {})
            }
            return formatted_response
        except Exception as e:
            raise Exception(f"Failed to parse response: {e}")

    def _parse_array_response(self, response):
        try:
            response = self._safejson(response)
            parsed_response = eval(response)
            formatted_response = {}
            for key, value in parsed_response.items():
                formatted_response[key] = {
                    "primary_topic": value.get("primary_topic", []),
                    "detailed_topic": value.get("detailed_topic", {}),
                    "sentiment": value.get("sentiment", {})
                }
            return formatted_response
        except Exception as e:
            raise Exception(f"Failed to parse response: {e}")

    @staticmethod
    def _flatten_topics(topics):
        flat_data = []
        for topic in topics:
            for t in topic.get('primary_topic', []):
                flat_data.append({
                    "primary_topic": t[0],
                    "sentiment": t[1]
                })
            for dt, subtopics in topic.get('detailed_topic', {}).items():
                for subtopic in subtopics:
                    flat_data.append({
                        "detailed_topic": dt,
                        "subtopic": subtopic
                    })
        return flat_data
    
    def to_dataframe(self, topics):
        flat_data = self._flatten_topics(topics)
        return pd.DataFrame(flat_data)