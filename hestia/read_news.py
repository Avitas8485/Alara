from news.newsapi import news_today, TODAYS_DATE
import json
from llm.news_llm import load_news_prompt, chat_completion
from text_to_speech.speech import TextToSpeechSystem


def clean_news_summary():
    # Load the news summary
    with open(f"hestia/news/news_summary/news_summary {TODAYS_DATE}.txt", "r") as file:
        news_summary = json.load(file)

    # Remove keys that are [Removed]
    news_summary = {k: v for k, v in news_summary.items() if k != "[Removed]"}

    for key, value in news_summary.items():
        # We only need title and summary, everything else is useless
        value.pop("url", None)
        value.pop("date", None)

        title = value.get("title", "")
        # remove unicode characters from title
        title = title.encode('ascii', 'ignore').decode('ascii')
        value["title"] = title

        # Clean up the summary
        summary = value.get("summary", "").replace("\n", "")
        # remove unicode characters from summary
        summary = summary.encode('ascii', 'ignore').decode('ascii')
        value["summary"] = summary
        
    # Write the cleaned up news summary to a file
    with open(f"hestia/news/news_summary/ {TODAYS_DATE}clean.txt", "w") as file:
        json.dump(news_summary, file, indent=4)
# Call the function


# Load the cleaned up news summary
def extract_simplified_news():
    with open(f"hestia/news/news_summary/ {TODAYS_DATE}clean.txt", "r") as file:
        news = json.load(file)
    # we only need the title
    news = [value["title"] for value in news.values()]
    # add a period at the end of each title
    news = [title + "." for title in news]
    # Write the simplified news to a file
    with open(f"hestia/news/news_summary/ {TODAYS_DATE}simplified.txt", "w") as file:
        file.write("\n".join(news))
        

def generate_news_summary():
    # load the news prompt
    news_prompt = load_news_prompt()
    # load the simplified news
    with open(f"hestia/news/news_summary/ {TODAYS_DATE}simplified.txt", "r") as file:
        news = file.read()
    # generate the news summary
    news_summary = chat_completion(news_prompt, news)["choices"][0]["message"]["content"]
    # write the news summary to a file
    with open(f"hestia/news/news_summary/ {TODAYS_DATE}summary.txt", "w") as file:
        file.write(news_summary)
    
# convert the news summary to speech
def convert_news_summary_to_speech():
    tts = TextToSpeechSystem()
    # load the news summary
    with open(f"hestia/news/news_summary/ {TODAYS_DATE}summary.txt", "r") as file:
        news_summary = file.read()
    # convert the news summary to speech
    tts.convert_text_to_speech_using_nlp(
        text=news_summary,
        output_dir="hestia/text_to_speech/outputs/news_summary",
        output_filename=f"{TODAYS_DATE}summary"
    )
    
     
        


    
if __name__ == '__main__':
    news_today()
    clean_news_summary()
    extract_simplified_news()
    generate_news_summary()
    convert_news_summary_to_speech()
