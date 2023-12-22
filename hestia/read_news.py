from news.newsapi import news_today, TODAYS_DATE
import json

def clean_news_summary():
    # Load the news summary
    with open(f"automation/news/news_summary/news_summary {TODAYS_DATE}.txt", "r") as file:
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
    with open(f"automation/news/news_summary/ {TODAYS_DATE}clean.txt", "w") as file:
        json.dump(news_summary, file, indent=4)
# Call the function


# Load the cleaned up news summary
def extract_simplified_news():
    with open(f"automation/news/news_summary/ {TODAYS_DATE}clean.txt", "r") as file:
        news = json.load(file)
    # we only need the title
    news = [value["title"] for value in news.values()]
    # add a period at the end of each title
    news = [title + "." for title in news]
    # Write the simplified news to a file
    with open(f"automation/news/news_summary/ {TODAYS_DATE}simplified.txt", "w") as file:
        file.write("\n".join(news))
        
    
     
        


    
if __name__ == '__main__':
    news_today()
    clean_news_summary()
    extract_simplified_news()
