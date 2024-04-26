import requests


class LlmServer:
    def __init__(self, url='http://localhost:8080/v1/chat/completions'):
        self.url = url
    
    def chat_completion(self, system_prompt, user_prompt, max_retries=3, grammar=None):
        for _ in range(max_retries):
            data = {
                'messages': [
                    {
                        'role': 'system',
                        'content': system_prompt
                    },
                    {
                        'role': 'user',
                        'content': user_prompt
                    }
                ],
                'max_tokens': 2048,
                'grammar': grammar
            }
            
            response = requests.post(self.url, json=data)
            
            if response.status_code == 200:
                response_json = response.json()
                return response_json['choices'][0]['message']['content']
            else:
                print('Failed to generate completion')
                
        print('Model failed to generate output after maximum retries.')
        return 'Model failed to generate output after maximum retries.'
        
