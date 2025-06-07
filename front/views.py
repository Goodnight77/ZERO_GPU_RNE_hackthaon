from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.conf import settings

def home(request):
    return render(request, 'rneClone/home.html')

def simulateur(request):
    return render(request, 'rneClone/SimulateurDenomination.html')

def Chatter(request):
    return render(request, 'rneClone/Chatbot.html')

@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            if not user_message:
                return JsonResponse({'error': 'No message provided'}, status=400)

            api_key = settings.LLM_API_KEY
            api_url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}'
            headers = {
                'Content-Type': 'application/json',
            }
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": user_message
                            }
                        ]
                    }
                ]
            }
            response = requests.post(api_url, headers=headers, json=payload)
            if response.status_code == 200:
                response_data = response.json()
                chatbot_reply = "Sorry, no response from chatbot."
                if 'candidates' in response_data and len(response_data['candidates']) > 0:
                    candidate = response_data['candidates'][0]['content']
                    # Extract the text from parts array
                    if 'parts' in candidate and len(candidate['parts']) > 0:
                        chatbot_reply = candidate['parts'][0].get('text', chatbot_reply)
                        # Remove trailing newline characters
                        chatbot_reply = chatbot_reply.rstrip('\n')
                    else:
                        chatbot_reply = candidate.get('content', chatbot_reply)
                return JsonResponse({'reply': chatbot_reply})
            else:
                return JsonResponse({'error': 'LLM API error'}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
