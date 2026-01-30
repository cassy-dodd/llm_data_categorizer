class Validator:
    def __init__(self, data):
        self.data = data
        self.errors = []

    def call(self):
        """Validate that response meets requirements"""
        
        if not isinstance(self.data, list):
            self.errors.append("Response must be a list")
            return self.errors
        
        for index, question in enumerate(self.data):
            if not isinstance(question, dict):
                self.errors.append(f"Question {index}: must be a dictionary")
                continue
            
            self._check_categories(question, index)
            self._check_answers(question, index)
        
        return self.errors
    
    def _check_categories(self, question, index):
        q_cats = question.get("question_categories", "")
        if isinstance(q_cats, list):
            self.errors.append(f"Question {index}: question_categories must be a single string, not a list")
        elif not q_cats:
            self.errors.append(f"Question {index}: missing question_categories")
    
    def _check_answers(self, question, index):
        """Check that answers exist and are valid"""
        answers = question.get("answers", [])
        if not answers:
            self.errors.append(f"Question {index}: no answers provided")
            return
        
        if not isinstance(answers, list):
            self.errors.append(f"Question {index}: answers must be a list")
            return
        
        for ans_index, answer in enumerate(answers):
            if not isinstance(answer, dict):
                self.errors.append(f"Question {index}, Answer {ans_index}: must be a dictionary")
                continue
            
            self._check_answer_categories(answer, index, ans_index)
            self._check_answer_values(answer, index, ans_index)
    
    def _check_answer_categories(self, answer, q_index, ans_index):
        """Check that answer_categories exist and are valid"""
        ans_cats = answer.get("answer_categories", [])
        if not ans_cats or (isinstance(ans_cats, list) and len(ans_cats) == 0):
            self.errors.append(f"Question {q_index}, Answer {ans_index}: missing answer_categories")
        elif not isinstance(ans_cats, list):
            self.errors.append(f"Question {q_index}, Answer {ans_index}: answer_categories must be a list")
    
    def _check_answer_values(self, answer, q_index, ans_index):
        """Check that answer_value exist and are valid"""
        ans_vals = answer.get("answer_value", [])
        if not ans_vals or (isinstance(ans_vals, list) and len(ans_vals) == 0):
            self.errors.append(f"Question {q_index}, Answer {ans_index}: missing answer_value")
        elif not isinstance(ans_vals, list):
            self.errors.append(f"Question {q_index}, Answer {ans_index}: answer_value must be a list")