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
            Create Questions Based on the file information:
                - Topic: {self.topic} (could be more than one topic. try to combine questions from the topics given or distribute all the topics evenly)
                - Multiple Choice Question Count (include multiple choice, true false, and multiple answer questions): {self.m_choice_number}
                - Essay Question Count : {self.essay_number}
                - Difficulty: {self.difficulty}
                - Language: {self.language} (If the value is "Book's Original", return all the questions in book's original language).

            Question Types:
                - Multiple Choice (m_choice): Four options with one correct answer.
                - Multiple Answer (m_answer): Select multiple correct answers.
                - True/False (m_choice): Decide if a statement is true or false.
                - Essay (essay): Requires a detailed written response.

            Difficulty Levels:
                - Beginner: Basic comprehension.
                - Intermediate: Application and easy to medium cases.
                - Expert: Critical thinking and analytical complex scenarios.
                - Combined: Combination of Beginner, Intermediate, and Expert.

            Return a List of JSON. Example:
            [
                (curly braces open)
                    "text": "Question text",
                    "options": ["option 1", "option 2", "option 3", "option 4"] (for true false type question, only return two options which is true and false),
                    "type": "m_choice" (follow the question type given above),
                    "correctOption": "option 1" for m_choice, list of strings for m_answer
                (curly braces close)
                ,
                ...
            ]
            Note : Return data EXACTLY like example above. Dont return more data than the requested above.
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
            check and decide if the user's answer to the question is correct or incorrect according to the file that has been given.

            this is the input data: 
                {self.answers}

            Return a List of JSON. Example:
            (curly braces open)
                answers: [
                            (curly braces open)
                                "question": "Question text",
                                "correctOption": (if the user's answer is correct, return the original user's answer. Otherwise, return the correct answer or improve the user's mistake in the answer. make it brief but clear, include source page number. You could rewrite exactly like the reference if the answer is exist)
                            (curly braces close)
                            ,
                            ...
                        ]
                correct_answers: (return the number of user's correct answers after checking)
            (curly braces close)
            Note :  If the given data is in Bahasa, return the corrected answer in Bahasa, otherwise return in English. 
            Return data EXACTLY like example above. Dont return more data than the requested above. Don't be strict and ignore case sensitive. try to compare user's answer and the reference from the file.
            '''


