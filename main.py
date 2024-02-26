'''from hestia.llm.llama_chat_completion import LlamaChatCompletion
from hestia.tts.piper_tts import PiperTTS
from hestia.stt.whisper_stt import StreamHandler
from hestia.stt.wakeword import WakeWord




system_prompt = "Your name is Alara. You are an AI assistant that helps people with their daily tasks." 
tts = PiperTTS()
handler = StreamHandler()
wake_word = WakeWord()
llm = LlamaChatCompletion()

# implementation a loop to keep the program running
while True:
    if wake_word.wake_word_detection():
        print("\033[96mWakeword detected..\033[0m")
        user_prompt = handler.listen()
        
        if user_prompt is None:
            user_prompt = ''

        output = llm.chat_completion(system_prompt, user_prompt)
        print(output)
        tts.synthesize(output)
        wake_word.clear_wakeword_buffer()
'''


from hestia.skills.news import News

news = News()
'''print(news.top_news())
print(news.news_in_category("science"))
print(news.latest_news())'''
print(news.call_feature("latest_news"))

