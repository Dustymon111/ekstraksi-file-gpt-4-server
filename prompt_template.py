class BookExtraction:
    description = 'You are a PDF file information retrieval assistant.'
    instruction = "You are a helpful assistant designed to output only JSON. retrieve the exact information from the file that has been given."
    bookExtractionTemplate = '''
                give me the exact title, author, and the lists and very brief description of TOC (if TOC exists) or topics from the file, desired output in json. example:
                {   
                    'title' : 'article or book or module title (usually Bold, largest font size, found in the first page)',
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
    instruction = "You are a helpful assistant designed to output only JSON. Process the information from the file that has been given to make questions with customized JSON output."

    def __init__(self, topic, m_choice_number, essay_number, difficulty):
        self.topic = topic
        self.m_choice_number = m_choice_number
        self.essay_number = essay_number
        self.difficulty = difficulty

    def questionMakerTemplate(self):
        return f'''
            Create Questions Based on the file information:
                - Topic: {self.topic}
                - Multiple Choice Question Count (include multiple choice, true false, and multiple answer questions): {self.m_choice_number}
                - Essay Question Count : {self.essay_number}
                - Difficulty: {self.difficulty}

            Question Types:
                - Multiple Choice (m_choice): Four options with one correct answer.
                - Multiple Answer (m_answer): Select multiple correct answers.
                - True/False (m_choice): Decide if a statement is true or false.
                - Essay (essay): Requires a detailed written response.

            Difficulty Levels:
                - Beginner: Basic comprehension.
                - Intermediate: Application and easy to medium cases.
                - Expert: Critical thinking and analytical complex scenarios.

            Return a List of JSON. Example:
            [
                (curly braces open)
                    "text": "Question text",
                    "options": ["option 1", "option 2", "option 3", "option 4"] (for true false type question, only return two options which is true and false),
                    "type": "m_choice" (follow the question type given above),
                    "correctOption": "option 1" (if the type is multiple answer, just append the text like this "option 1option 2option 3"")
                (curly braces close)
                ,
                ...
            ]
            Note : For essay questions, "options" return [] and "correctOption" return "".
            Ensure questions match the difficulty level and stay relevant to the topic.
            '''.format(self.topic, self.m_choice_number, self.essay_number, self.difficulty)


