class BookExtraction:
    description = 'You are a PDF file information retrieval assistant.'
    instruction = "You are a helpful assistant designed to output only JSON. retrieve the exact information from the file that has been given."
    bookExtractionTemplate = '''
                give me the exact title, author, and the lists and very brief description of TOC (if TOC exists) or topics from the file, desired output in json. example:
                {   
                    'title' : 'article or book or module title (usually Bold, found in the first page)',
                    'author' : ['author', ...] (full name, if exists, could be on "edited by", or "written by". if doesn't exist, return [N/A]),
                    'topics': [
                    {
                        "title": 'Introduction',
                        "description": "this is the introduction..."
                    },
                    {
                        "title": 'methodology',
                        "description": "..." 
                    },
                    ...]
                }
                '''



class QuestionMaker:
    description = 'You are a question maker assistant.'
    instruction = "You are a helpful assistant designed to output only JSON. process the information from the file that has been given to make questions with customized JSON output."

    def __init__(self, topic, number, difficulty):
        self.topic = topic
        self.number = number
        self.difficulty = difficulty
        self.questionMakerTemplate = f'''
               Create Questions Based on the file's:
                Topic: {self.topic}
                Number: {self.number}
                Difficulty: {self.difficulty}
                Question Types:

                Multiple Choice (m_choice): Four options with one correct answer.
                Multiple Answer (m_answer): Select multiple correct answers.
                True/False (m_choice): Decide if a statement is true or false.
                Essay (essay): Requires a detailed written response.
                Difficulty Levels:

                Beginner: Basic comprehension.
                Intermediate: Application and easy to medium cases.
                Expert: Critical thinking and complex scenarios.
                Example:

                json
                {{
                    "text": "Question text",
                    "options": ["A. option 1", "B. option 2", "C. option 3", "D. option 4"],
                    "type": "m_choice",
                    "correctOption": "A. option 1"
                }}
                Ensure questions match the difficulty level and stay relevant to the topic.
                '''

# # Example of using the class
# topic = "Mathematics"
# number = 10
# difficulty = "Intermediate"

# question_maker = QuestionMaker(topic, number, difficulty)
# print(question_maker.questionMakerTemplate)
