from hestia.llm.llama_chat_completion import chat_completion
from hestia.tts.piper_tts import PiperTTS
from hestia.stt.whisper_stt import StreamHandler
from hestia.stt.wakeword import WakeWord




system_prompt = "Your name is Alara. You are an AI assistant that helps people with their daily tasks." 
tts = PiperTTS()
handler = StreamHandler()
wake_word = WakeWord()
if wake_word.wake_word_detection():
    print("\033[96mWakeword detected..\033[0m")
    user_prompt = handler.listen()

    if isinstance(user_prompt, list):
        user_prompt = ' '.join(user_prompt)
    elif user_prompt is None:
        user_prompt = ''

    output = chat_completion(system_prompt, user_prompt)
    print(output)
    tts.synthesize(output)