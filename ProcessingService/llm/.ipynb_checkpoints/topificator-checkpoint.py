import requests

class TopicExtractor:
    def __init__(self, model="llama3", url='http://localhost:11434/api/generate'):
        self.url = url
        self.model = model
        self.format1 = "{ \
            primary_topic: [('xxx', 'Positive'), ('xxx', 'Negative'), ('xxx', 'Neutral')], \
            detailed_topic: {'xxx':['subtopic1', 'subtopic2', ...]} \
        }"
        self.format2 = "{ \
            1: {primary_topic: [('xxx', 'Positive'), ('xxx', 'Negative'), ('xxx', 'Neutral')], \
                detailed_topic: {'xxx': ['subtopic1', 'subtopic2', ...]} }, \
            2: {primary_topic: [('xxx', 'Positive'), ('xxx', 'Negative'), ('xxx', 'Neutral')], \
                detailed_topic: {'xxx': ['subtopic1', 'subtopic2', ...]} }, \
            3: ... \
        }"

    def _send_request(self, prompt):
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(self.url, json=data)
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get('response', 'No response field found')
        else:
            raise Exception(f"Failed to retrieve data, status code {response.status_code}")
    
    def extract(self, reviews, type='SINGLE_SOURCE'):
        if type == 'SINGLE_SOURCE':
            if isinstance(reviews, str):
                prompt = f"Extract topic from this review '{reviews}'. And output in this format: " + self.format1 + " Give just json Output. No extra comment."
                response = self._send_request(prompt)
                return self._parse_single_response(response)
            else:
                raise AssertionError("For SINGLE_SOURCE, reviews should be a single string.")
        elif type == 'MULTI_SOURCE':
            if isinstance(reviews, list):
                combined_reviews = " -- ".join(reviews)
                prompt = f"Extract topics from these reviews '{combined_reviews}'. And output in this format: " + self.format2 + " Give just json Output. No extra comment."
                response = self._send_request(prompt)
                return self._parse_array_response(response)
            else:
                raise AssertionError("For MULTI_SOURCE, reviews should be a list of strings.")
        else:
            raise AssertionError("type arg should either be 'SINGLE_SOURCE' or 'MULTI_SOURCE'")
        
    @staticmethod
    def _safejson(response):
            first_brace = response.find('{')
            last_brace = response.rfind('}')
            if first_brace == -1 or last_brace == -1:
                raise ValueError("No JSON object could be identified in the response")
            return response[first_brace:last_brace + 1]
        
    @staticmethod
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
