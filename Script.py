import os
import json
import sqlite3
import time
from typing import List, Dict, Tuple, Optional
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

# Load environment variables
load_dotenv()

class LanguageLearningBot:
    """A chatbot that helps users learn languages through immersive conversation."""

    # Available scenes for practice
    SCENES = {
        "restaurant": "You are at a restaurant ordering food and chatting with the waiter/waitress.",
        "hotel": "You are checking into a hotel and talking with the receptionist.",
        "shopping": "You are shopping for clothes and asking questions to a shop assistant.",
        "airport": "You are at the airport asking for information about your flight.",
        "doctor": "You are visiting a doctor and explaining your symptoms.",
        "job_interview": "You are being interviewed for a job position.",
        "making_friends": "You are meeting someone new and trying to make friends.",
        "public_transport": "You are asking for directions on public transportation."
    }

    # Available language levels
    LEVELS = ["beginner", "intermediate", "advanced"]

    def __init__(self, db_path: str = "language_learning.db"):
        """Initialize the bot with a database connection and OpenAI client."""
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Initialize LangChain components
        self.chat_model = ChatOpenAI(
            temperature=0.7,
            model="gpt-4o"
        )

        # Setup database
        self.db_path = db_path
        self.setup_database()

        # Session data
        self.user_id = None
        self.target_language = None
        self.native_language = None
        self.proficiency_level = None
        self.selected_scene = None
        self.session_id = None
        self.mistakes = []

        # Conversation memory
        self.memory = ConversationBufferMemory(return_messages=True)

    def setup_database(self):
        """Set up the SQLite database with necessary tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create sessions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            target_language TEXT,
            native_language TEXT,
            proficiency_level TEXT,
            scene TEXT,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')

        # Create mistakes table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS mistakes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            mistake_text TEXT,
            correction TEXT,
            mistake_type TEXT,
            importance INTEGER,
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
        ''')

        conn.commit()
        conn.close()

    def create_user(self) -> int:
        """Create a new user in the database and return the user ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users DEFAULT VALUES")
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id

    def start_session(self) -> int:
        """Start a new learning session and return the session ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO sessions (user_id, target_language, native_language, proficiency_level, scene)
        VALUES (?, ?, ?, ?, ?)
        ''', (self.user_id, self.target_language, self.native_language, self.proficiency_level, self.selected_scene))
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return session_id

    def end_session(self):
        """End the current learning session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE sessions 
        SET end_time = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (self.session_id,))
        conn.commit()
        conn.close()

    def record_mistake(self, mistake_text: str, correction: str, mistake_type: str, importance: int = 1):
        """Record a user mistake in the database."""
        self.mistakes.append({
            "mistake_text": mistake_text,
            "correction": correction,
            "mistake_type": mistake_type,
            "importance": importance
        })

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO mistakes (session_id, mistake_text, correction, mistake_type, importance)
        VALUES (?, ?, ?, ?, ?)
        ''', (self.session_id, mistake_text, correction, mistake_type, importance))
        conn.commit()
        conn.close()

    def get_available_languages(self) -> List[str]:
        """Return a list of available languages for learning."""
        # Using common languages that OpenAI models can handle well
        return [
            "Spanish", "French", "German", "Italian", "Portuguese",
            "Russian", "Japanese", "Chinese", "Korean", "Arabic",
            "Hindi", "Dutch", "Swedish", "Turkish", "Polish"
        ]

    def get_language_preference(self) -> Tuple[str, str]:
        """Ask the user about their language preferences."""
        print("Welcome to the Language Learning Bot!")

        # Get the target language
        available_languages = self.get_available_languages()
        print("\nAvailable languages for learning:")
        for i, lang in enumerate(available_languages, 1):
            print(f"{i}. {lang}")

        while True:
            try:
                choice = int(input("\nWhich language would you like to learn? (Enter the number): "))
                if 1 <= choice <= len(available_languages):
                    target_language = available_languages[choice - 1]
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

        # Get the native language
        native_language = input("\nWhat is your native language? ").strip()

        return target_language, native_language

    def get_proficiency_level(self) -> str:
        """Ask the user about their proficiency level in the target language."""
        print("\nPlease select your proficiency level in " + self.target_language + ":")
        for i, level in enumerate(self.LEVELS, 1):
            print(f"{i}. {level.capitalize()}")

        while True:
            try:
                choice = int(input("\nEnter the number of your level: "))
                if 1 <= choice <= len(self.LEVELS):
                    return self.LEVELS[choice - 1]
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

    def select_scene(self) -> str:
        """Ask the user to select a conversation scene."""
        print("\nPlease select a conversation scenario to practice:")
        for i, (scene, description) in enumerate(self.SCENES.items(), 1):
            print(f"{i}. {scene.replace('_', ' ').title()}: {description}")

        while True:
            try:
                choice = int(input("\nEnter the number of the scene: "))
                if 1 <= choice <= len(self.SCENES):
                    scene_key = list(self.SCENES.keys())[choice - 1]
                    return scene_key
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

    def create_scene_system_prompt(self) -> str:
        """Create a system prompt for the scene based on user preferences."""
        scene_description = self.SCENES[self.selected_scene]

        system_prompt = f"""
        You are an AI language tutor helping someone learn {self.target_language}. 
        Their native language is {self.native_language} and their level is {self.proficiency_level}.

        Scene: {scene_description}

        You will play the role of a native {self.target_language} speaker in this scene.

        Guidelines:
        1. Primarily use {self.target_language}, but adapt your language complexity to their {self.proficiency_level} level.
        2. For beginner: Use simple phrases, speak slowly, and provide translations to {self.native_language} when needed.
        3. For intermediate: Use everyday language, occasionally provide translations for difficult words.
        4. For advanced: Use natural, native-like speech with occasional challenging vocabulary.
        5. When the user makes mistakes, gently correct them in your response. When you correct them, format the correction as: [Correction: original mistake → corrected version].
        6. Track the user's common mistakes and areas for improvement.
        7. Be patient, encouraging, and make the conversation natural and engaging.
        8. Start the conversation naturally as if you are in the scene described.

        Begin the conversation in {self.target_language}, introducing yourself according to the scene and asking a question to engage the user.
        """

        return system_prompt

    def analyze_user_response(self, user_input: str) -> Dict:
        """Analyze the user's message for mistakes using OpenAI."""
        prompt = f"""
        Analyze the following message in {self.target_language} from a {self.proficiency_level} level student:

        "{user_input}"

        Identify any mistakes with grammar, vocabulary, sentence structure, or idioms.
        For each mistake, provide:
        1. The incorrect text
        2. The corrected version
        3. A brief explanation of the rule or why it's incorrect
        4. The type of mistake (grammar, vocabulary, structure, idiom, etc.)
        5. Importance (1-3, where 3 is a critical mistake)

        Format your response as a JSON object like this:
        {{
            "mistakes": [
                {{
                    "incorrect": "mistake text",
                    "correction": "corrected text",
                    "explanation": "brief explanation",
                    "type": "grammar/vocabulary/etc",
                    "importance": 2
                }}
            ],
            "overall_quality": 1-5 rating of the response,
            "strengths": ["strength1", "strength2"],
            "improvement_areas": ["area1", "area2"]
        }}

        If there are no mistakes, return an empty array for mistakes.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        try:
            analysis = json.loads(response.choices[0].message.content)
            return analysis
        except Exception as e:
            print(f"Error parsing analysis response: {e}")
            return {"mistakes": [], "overall_quality": 3, "strengths": [], "improvement_areas": []}

    def prepare_chat_response(self, user_input: str, analysis: Dict) -> str:
        """Create an appropriate response to the user based on analysis."""
        # Create prompt for the language tutor response
        correction_text = ""
        for mistake in analysis.get("mistakes", []):
            if mistake["importance"] >= 2:  # Only correct important mistakes
                correction_text += f"[Correction: {mistake['incorrect']} → {mistake['correction']}]\n"
                # Record the mistake in the database
                self.record_mistake(
                    mistake_text=mistake["incorrect"],
                    correction=mistake["correction"],
                    mistake_type=mistake["type"],
                    importance=mistake["importance"]
                )

        # Create prompt for chat response
        prompt = f"""
        The user (a {self.proficiency_level} {self.target_language} learner) said:
        "{user_input}"

        You are a native {self.target_language} speaker in this scene: {self.SCENES[self.selected_scene]}

        Continue the conversation naturally. Respond in {self.target_language} appropriate for their level.

        After your response in {self.target_language}, provide these corrections if needed:
        {correction_text}

        Keep your response conversational and appropriate to the scene.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.create_scene_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        return response.choices[0].message.content

    def generate_session_feedback(self) -> str:
        """Generate comprehensive feedback for the learning session."""
        if not self.mistakes:
            return "Great job! You didn't make any significant mistakes in this conversation."

        # Create a dataframe from the mistakes for analysis
        df = pd.DataFrame(self.mistakes)

        # Prepare data for feedback generation
        mistake_types = df["mistake_type"].value_counts().to_dict()
        important_mistakes = df[df["importance"] >= 2].to_dict("records")

        # Create the feedback prompt
        prompt = f"""
        Generate comprehensive feedback for a {self.proficiency_level} level {self.target_language} learner whose native language is {self.native_language}.

        The user had a conversation in a "{self.selected_scene}" scenario.

        Here's an analysis of their mistakes:
        - Mistake types: {mistake_types}
        - Important mistakes: {important_mistakes}

        Provide:
        1. A short overall assessment
        2. 2-3 specific areas where they should focus on improving
        3. 2-3 strengths they demonstrated 
        4. Specific practice exercises they could do to address their errors
        5. Common words/phrases they struggled with (if applicable)

        Make the feedback encouraging but constructive.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return response.choices[0].message.content

    def run(self):
        """Run the language learning bot with the full workflow."""
        # Create a new user
        self.user_id = self.create_user()

        # Get user preferences
        self.target_language, self.native_language = self.get_language_preference()
        self.proficiency_level = self.get_proficiency_level()
        self.selected_scene = self.select_scene()

        # Start a new session
        self.session_id = self.start_session()

        # Build the LangChain components with conversation memory
        system_message = SystemMessage(content=self.create_scene_system_prompt())

        # Create chain for initial message
        initial_prompt = ChatPromptTemplate.from_messages([system_message])
        initial_chain = LLMChain(
            llm=self.chat_model,
            prompt=initial_prompt
        )

        # Send initial message
        intro_message = initial_chain.run({})
        print("\n\n" + intro_message + "\n")

        # Conversation loop
        try:
            while True:
                # Get user input
                user_input = input("> ")

                # Check for exit command
                if user_input.lower() in ["exit", "quit", "bye"]:
                    break

                # Analyze user input for mistakes
                analysis = self.analyze_user_response(user_input)

                # Generate bot response
                bot_response = self.prepare_chat_response(user_input, analysis)
                print("\n" + bot_response + "\n")

                # Update conversation memory
                self.memory.chat_memory.add_user_message(user_input)
                self.memory.chat_memory.add_ai_message(bot_response)

        except KeyboardInterrupt:
            print("\nEnding conversation...")

        # End session and provide feedback
        self.end_session()
        print("\n\n--- Session Feedback ---")
        feedback = self.generate_session_feedback()
        print(feedback)

        # Print mistake summary
        if self.mistakes:
            print("\n--- Mistake Summary ---")
            df = pd.DataFrame(self.mistakes)

            # Group mistakes by type
            mistake_types = df["mistake_type"].value_counts()
            print("\nMistake Types:")
            for mistake_type, count in mistake_types.items():
                print(f"- {mistake_type}: {count}")

            # Show the most important mistakes
            important_mistakes = df[df["importance"] >= 2].sort_values("importance", ascending=False)
            if len(important_mistakes) > 0:
                print("\nTop Mistakes to Focus On:")
                for _, row in important_mistakes.iterrows():
                    print(f"- {row['mistake_text']} → {row['correction']} ({row['mistake_type']})")

        print("\nThank you for practicing with the Language Learning Bot!")


if __name__ == "__main__":
    # Create and run the bot
    bot = LanguageLearningBot()
    bot.run()