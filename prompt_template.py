class BookExtraction:
    description = 'You are a PDF file information retrieval assistant.'
    instruction = "You are a helpful assistant designed to output only JSON. retrieve the exact information from the file that has been given."
    bookExtractionTemplate = '''
                give me the exact title, author, and the lists and very brief description of TOC (if TOC exists) or topics from the file, desired output in json. example:
                {   
                    'title' : 'article or book or module title (usually Bold, largest font size, found in the first page)',
                    'author' : ['author', ...] (return full name, could be on "edited by", or "written by". if doesn't exist, return [N/A]),
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
                Note: Return data EXACTLY like the example above. Dont return more data than the requested above.
                Reference, foreword, thank you note doesn't need to be added to the topics
                '''
                



class QuestionMaker:
    description = 'You are a question maker assistant.'
    instruction = "You are a helpful assistant designed to output only JSON. Process the information from the file that has been given to make questions with customized JSON output."

    def __init__(self, topic, m_choice_number, essay_number, difficulty, language):
        self.topic = topic
        self.m_choice_number = m_choice_number
        self.essay_number = essay_number
        self.difficulty = difficulty
        self.language = language

    def questionMakerTemplate(self):
        return f'''
            Task: Generate questions from the given file content.

            Parameters:
                Topic: {self.topic} (Distribute questions evenly across all topics. If the total number of questions doesn't divide evenly, assign the extra questions to the first topics in the list.)
                Question Count:
                    Multiple Choice (m_choice), True/False, Multiple Answer: {self.m_choice_number}
                    Essay: {self.essay_number}
                Difficulty: {self.difficulty} (For "Combined," distribute 33.3% Beginner, 33.3% Intermediate, and 33.3% Expert)
                Language: {self.language} (For "Book's Original", returns questions in the book's language)

            Question Types:
                Multiple Choice (m_choice): consist of four options, only one option is correct.
                True/False (m_choice): Two options: True, False. (same type as the multiple choice)
                Multiple Answer (m_answer): consisting of four options, Multiple correct options.
                Essay (essay): Requires a written response.

            Return a List of JSON. Example:
            [
                (curly braces open)
                    "text": "Question text",
                    "options": ["option 1", "option 2", "option 3", "option 4"] (for true false type question, only return two options which is true and false),
                    "type": "m_choice" (follow the question type given above),
                    "correctOption": "option 1" for m_choice, list of strings for m_answer,
                    "difficulty" : question's difficulty level,
                (curly braces close)
                ,
                ...
            ]
            Note : 
            True/False returns the same type as multiple choice, which is m_choice.
            Return data EXACTLY like example above. Dont return more data than the requested above.
            For essay questions, "options" return [] and "correctOption" return "".
            Ensure questions match the difficulty level and stay relevant to the topic, and ensure the returned type and the question type followed the rule above.
            '''.format(self.topic, self.m_choice_number, self.essay_number, self.difficulty, self.language)
    

class EssayChecker:
    description = 'You are a Essay Checker assistant.'
    instruction = "You are a helpful assistant designed to output only JSON. Process the information from the file that has been given to check user's answer with customized JSON output."

    def __init__(self, answers):
        self.answers = answers

    def essayCheckerTemplate(self):
        return f'''
            The given data could be in English or Bahasa.
            You will be given a list of objects of user's answers according to the essay questions. input example: 
            [
                (curly braces open)
                    "question" : "Explain what is 2nd newton's rule",
                    "answer" : "Newton 2nd rule is explaining about ...."
                (curly braces close),
                ...
            ]
            this is the input data: 
                {self.answers}
            
            Your task is to:
                1. Check if the user's answer is correct or incorrect based on the given file. If the user's answer is close to the correct answer, consider it correct.
                2. Return a JSON list with the following structure:

            (curly braces open)
                answers: [
                            (curly braces open)
                                "question": "Question text",
                                "correctOption": (if the user's answer is correct, return the EXACT original user's answer. If the user's answer is incorrect, return the correct answer as similar as possible to the reference. Make it brief and clear, following the reference if necessary),
                                "correct": (boolean, if the user's answer is correct, return true; otherwise, return false)
                            (curly braces close)
                            ,
                            ...
                        ]
                correct_answers: (return the number of user's correct answers after checking)
            (curly braces close)

            Note:
                - Be explicit: if the answer is correct, do not rewrite or alter the original user's answer; simply return it as is.
                - If the given data is in Bahasa, return in Bahasa. Otherwise, return in English.
                - Do not return more data than the requested above. 
                - Be flexible, Ignore case sensitivity or a little bit of typo.
            '''


