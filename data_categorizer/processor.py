from ollama import chat
from .prompter import Prompter
import pandas as pd
import json
import time
import re

class Processor:
    CHUNK_SIZE = 5
    MAX_RETRY_COUNT = 2

    def __init__(self, input_file, output_file, model_name):
        self.input_file = input_file
        self.output_file = output_file
        self.model_name = model_name

    def call(self):
        df = pd.read_csv(self.input_file)
        chunks = [df.iloc[i:i + self.CHUNK_SIZE] for i in range(0, len(df), self.CHUNK_SIZE)]
        output_rows = []


        for chunk in chunks:
            results, error = self._process_chunk_with_retry(chunk)
            
            if error:
                print(f"Skipping chunk due to error: {error}")
                continue
            
            if not results:
                print("No results returned, skipping chunk")
                continue
            
            for question in results:
                # Safety check
                if not isinstance(question, dict):
                    print(f"Skipping malformed question: {question}")
                    continue
                
                q_text = question.get("question_text")
                q_cats = question.get("question_categories", "")
                
                # Ensure question_categories is a string
                if isinstance(q_cats, list):
                    q_cats = q_cats[0] if q_cats else ""
                
                answers = question.get("answers", [])
                if not isinstance(answers, list):
                    print(f"Skipping question with invalid answers: {q_text}")
                    continue
                
                for answer in answers:
                    # Safety check
                    if not isinstance(answer, dict):
                        print(f"Skipping malformed answer: {answer}")
                        continue
                    
                    # Ensure lists for categories and values
                    ans_cats = answer.get("answer_categories", [])
                    ans_vals = answer.get("answer_value", [])
                    
                    if not isinstance(ans_cats, list):
                        ans_cats = [ans_cats] if ans_cats else []
                    if not isinstance(ans_vals, list):
                        ans_vals = [ans_vals] if ans_vals else []
                    
                    output_rows.append({
                        "question_text": q_text,
                        "question_categories": q_cats,
                        "answer_text": answer.get("answer_text"),
                        "answer_categories": ";".join(str(c) for c in ans_cats),
                        "answer_value": ";".join(str(v) for v in ans_vals)
                    })
                print(f"Processed question with category: {q_cats}")
    
            time.sleep(0.5)
        
        self._export_csv(output_rows)

    def _extract_json(self, text):
        """Extract JSON from response, handling markdown code blocks"""
        json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', text, re.DOTALL)
        if json_match:
            return json_match.group(1)
        
        json_match = re.search(r'(\[.*\])', text, re.DOTALL)
        if json_match:
            return json_match.group(1)
        
        return text
    
    def _validate_response(self, results):
        """Validate that response meets requirements"""
        errors = []
        
        # Check if results is a list
        if not isinstance(results, list):
            errors.append("Response must be a list")
            return errors
        
        for idx, question in enumerate(results):
            # Check if question is a dict
            if not isinstance(question, dict):
                errors.append(f"Question {idx}: must be a dictionary")
                continue
            
            # Check question has single category (string, not list)
            q_cats = question.get("question_categories", "")
            if isinstance(q_cats, list):
                errors.append(f"Question {idx}: question_categories must be a single string, not a list")
            elif not q_cats:
                errors.append(f"Question {idx}: missing question_categories")
            
            # Check answers exist and are valid
            answers = question.get("answers", [])
            if not answers:
                errors.append(f"Question {idx}: no answers provided")
                continue
            
            if not isinstance(answers, list):
                errors.append(f"Question {idx}: answers must be a list")
                continue
            
            for ans_idx, answer in enumerate(answers):
                # Check if answer is a dict
                if not isinstance(answer, dict):
                    errors.append(f"Question {idx}, Answer {ans_idx}: must be a dictionary")
                    continue
                
                # Check answer has categories
                ans_cats = answer.get("answer_categories", [])
                if not ans_cats or (isinstance(ans_cats, list) and len(ans_cats) == 0):
                    errors.append(f"Question {idx}, Answer {ans_idx}: missing answer_categories")
                
                # Check answer has values
                ans_vals = answer.get("answer_value", [])
                if not ans_vals or (isinstance(ans_vals, list) and len(ans_vals) == 0):
                    errors.append(f"Question {idx}, Answer {ans_idx}: missing answer_value")
                
                # Ensure answer_categories and answer_value are lists
                if ans_cats and not isinstance(ans_cats, list):
                    errors.append(f"Question {idx}, Answer {ans_idx}: answer_categories must be a list")
                if ans_vals and not isinstance(ans_vals, list):
                    errors.append(f"Question {idx}, Answer {ans_idx}: answer_value must be a list")
        
        return errors
    
    def _process_chunk_with_retry(self, chunk):
        """Process chunk with retry logic"""
        for attempt in range(self.MAX_RETRY_COUNT):
            prompt = Prompter(chunk).call()

            response = chat(model=self.model_name, messages=[{'role': 'user', 'content': prompt}])
            
            try:
                response_text = response['message']['content']
                print(f"Attempt {attempt + 1} - Raw response preview: {response_text[:200]}...")
                
                json_text = self._extract_json(response_text)
                results = json.loads(json_text)
                
                validation_errors = self._validate_response(results)
                if validation_errors:
                    print(f"Validation errors on attempt {attempt + 1}:")
                    for error in validation_errors:
                        print(f"  - {error}")
                    if attempt < self.MAX_RETRY_COUNT - 1:
                        print("Retrying...")
                        time.sleep(1)
                        continue
                    else:
                        print("Max retries reached, using best effort...")
                
                return results, None
                
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error on attempt {attempt + 1}: {e}")
                if attempt < self.MAX_RETRY_COUNT - 1:
                    print("Retrying...")
                    time.sleep(1)
                else:
                    return None, f"Failed after {self.MAX_RETRY_COUNT} attempts: {e}"
        
        return None, "Max retries exceeded"
    
    def _export_csv(self, output_rows):
        output_df = pd.DataFrame(output_rows)
        output_df.to_csv("survey_categorized5.csv", index=False)
        print("✅ CSV saved: survey_categorized5.csv")