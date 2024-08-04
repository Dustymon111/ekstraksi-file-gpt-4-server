class BookExtraction:
    description = 'You are a PDF file information retrieval assistant.'
    instruction = "You are a helpful assistant designed to output only JSON. process the information from the file that has been given to extract the TOC."
    bookExtractionTemplate = '''
                give me the title, author, and the lists and very brief description of TOC (if exists) or topics from the file, desired output in json. example:
                {   
                    'title' : 'article or book or module title (usually Bold)',
                    'author' : ['author', ...] (try to find the full name, if exists),
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
    questionMakerTemplate ='''
               Create Questions Based on the file's:
                Topic: {}
                Number: {Number of Questions}
                Difficulty: {Difficulty Level}
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
                {
                    "text": "Question text",
                    "options": ["A. option 1", "B. option 2", "C. option 3", "D. option 4"],
                    "type": "m_choice",
                    "correctOption": "A. option 1"
                }
                Ensure questions match the difficulty level and stay relevant to the topic.
                '''