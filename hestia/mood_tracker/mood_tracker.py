import datetime
import yaml
import sqlite3


class MoodTracker:
    def __init__(self):
        self.conn = sqlite3.connect('mood_tracker/mood_tracker.db')
        self.cursor = self.conn.cursor()
        self.create_mood_table()
        with open('mood_tracker/emotions_advanced.yaml', 'r') as file:
            self.emotions = yaml.load(file, Loader=yaml.FullLoader)['Emotions']
    
    def create_mood_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS mood (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                emotion TEXT NOT NULL,
                sub_emotion TEXT NOT NULL,
                speficity TEXT NOT NULL
            )
            """
        )
    def select_emotion(self, emotions: list):
        for index, emotion in enumerate(emotions,start=1):
            print(f"{index}. {emotion['emotion']}")
        selection = int(input("Select an emotion: "))
        if selection not in range(1, len(emotions) + 1):
            print(f"Invalid selection, please select a number between 1 and {len(emotions)}")
            return self.select_emotion(emotions)
        return emotions[selection - 1]
    
    def track_mood(self):
        emotion = self.select_emotion(self.emotions)
        sub_emotion = self.select_emotion(emotion['sub_emotions'])
        speficity = self.select_emotion(sub_emotion['sub_emotions'])
        
        return {"emotion": emotion,
                "sub_emotion": sub_emotion,
                "speficity": speficity}
    
    def record_mood(self, emotions: list):
        mood = self.track_mood()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        mood_entry = {
            "timestamp": timestamp,
            "emotion": mood['emotion']['emotion'],
            "sub_emotion": mood['sub_emotion']['emotion'],
            "speficity": mood['speficity']['emotion']
        }
        self.cursor.execute(
            """
            INSERT INTO mood (timestamp, emotion, sub_emotion, speficity)
            VALUES (:timestamp, :emotion, :sub_emotion, :speficity)
            """,
            mood_entry
        )
    
    def display_mood_entries(self):
        self.cursor.execute(
            """
            SELECT * FROM mood
            """
        )
        mood_entries = self.cursor.fetchall()
        for mood_entry in mood_entries:
            print(mood_entry)


def main():
    mood_tracker = MoodTracker()
    mood_tracker.record_mood(mood_tracker.emotions)
    mood_tracker.display_mood_entries()
    
if __name__ == '__main__':
    main()
    
    