# 🌍 Language Learning Bot

A conversational AI assistant designed to help users practice languages through immersive, real-world conversation scenarios like visiting a restaurant, going to the airport, or attending a job interview.

Built using OpenAI's GPT-4 and LangChain, it tracks user progress, corrects mistakes, and stores data using an SQLite database.

---

## 🚀 Features

- **Immersive Practice Scenes**: Simulate real-world scenarios like restaurants, hotels, shopping, and more.
- **Multilingual Support**: Learn 15+ languages with personalized difficulty based on user proficiency.
- **Error Detection & Correction**: Real-time grammar and vocabulary corrections with explanations.
- **Session Tracking**: Automatically logs user sessions and mistake history.
- **Persistent Memory**: Tracks and learns from previous interactions using LangChain's memory.
- **OpenAI GPT-4o Integration**: Uses the latest `gpt-4o` model for natural and adaptive conversation.

---

## 📂 Project Structure

```
language-learning-bot/
│
├── Script.py                   # Core chatbot implementation
├── .env                      # Stores your OpenAI API Key
├── language_learning.db      # SQLite database created on runtime
└── README.md                 # Project documentation
```

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/language-learning-bot.git
cd language-learning-bot
```

### 2. Install Dependencies

Make sure you have Python 3.8+ installed.

```bash
pip install -r requirements.txt
```

Required packages include:
- `openai`
- `langchain`
- `python-dotenv`
- `pandas`

> Note: Add these to `requirements.txt` if not already created.

### 3. Set up OpenAI API Key

Create a `.env` file in the root directory with the following content:

```
OPENAI_API_KEY=your_openai_api_key_here
```

---

## 💬 How It Works

1. **Start the bot** and enter your language preferences.
2. **Choose a scene** like restaurant, hotel, or job interview.
3. The bot **converses naturally** in your target language based on your level.
4. It **analyzes your input**, corrects mistakes, and stores them in a local database.
5. You can review your **strengths, improvement areas**, and overall performance.

---

## 🧠 Conversation Flow

- **Memory**: Tracks ongoing conversation context using `ConversationBufferMemory`.
- **Mistake Tracking**: Saves each mistake with metadata (type, correction, importance).
- **Scene Simulation**: Dynamic prompts based on selected real-world scene.

---

## 🗃️ Database Structure

SQLite is used to store:
- **Users**
- **Sessions**
- **Mistakes**

| Table      | Description                        |
|------------|------------------------------------|
| users      | Stores user IDs and timestamps     |
| sessions   | Logs user sessions and settings    |
| mistakes   | Records mistakes and corrections   |

---

## 📌 Supported Languages

- Spanish
- French
- German
- Italian
- Portuguese
- Russian
- Japanese
- Chinese
- Korean
- Arabic
- Hindi
- Dutch
- Swedish
- Turkish
- Polish

---

## 🧪 Example Usage

```python
bot = LanguageLearningBot()
bot.user_id = bot.create_user()
bot.target_language, bot.native_language = bot.get_language_preference()
bot.proficiency_level = bot.get_proficiency_level()
bot.selected_scene = bot.select_scene()
bot.session_id = bot.start_session()

# Begin conversation with system prompt
prompt = bot.create_scene_system_prompt()
print(prompt)

# Analyze user response
response = bot.analyze_user_response("Je suis aller à la restaurant hier.")
print(response)
```

---

## 🧑‍💻 Author

**Tanish Ashtekar**  
_Data Science Associate & AI/ML Developers/Enginner_

---

## 📄 License

MIT License - feel free to use and modify.
