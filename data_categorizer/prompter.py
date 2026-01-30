import json

class Prompter:
    def __init__(self, data_chunk) -> None:
        self.data_chunk = data_chunk

    def call(self):
        prompt_text = '''You are a survey categorization assistant with medical knowledge.
        CRITICAL RULES:
        1. Return ONLY valid JSON, no explanations or markdown
        2. ALL categories and values MUST be in English only
        3. Each question gets EXACTLY ONE category (not a list)
        4. Each answer MUST have at least one category and one value (can be a list)
        5. Translate German terms to English (e.g., Haarausfall → hair_loss)
        6. For questions, summarize the main semantic meaning of the string into a category
        7. Within answers array, 'operand' is the user facing answer.
        
        JSON Format (follow exactly):
        [
        {
            "question_text": "exact question text here",
            "question_categories": "single_category_here",
            "answers": [
            {
                "answer_text": "exact answer text",
                "answer_categories": ["frequency", "intensity"],
                "answer_value": ["often", "high"]
            }
            ]
        }
        ]
        
        CATEGORIZATION RULES:
        - Question categories: (example cateogries) smoking, alcohol, exercise, diet, sleep, stress, medication, medical_history, demographics, symptoms, bmi, instruction, acknowledgement, consent
        - Answer categories: (example cateogries) frequency, quantity, severity, duration, boolean, scale, N/A
        - Answer values: (example values) low/medium/high, often/sometimes/rarely/never, true/false, mild/moderate/severe, none, 0-10

        GOAL:
        - the aim is to be able to categorize this data into meaningful, measurable buckets and to exclude those which are not measurable via dfferent categories such as N/A.
        
        EXAMPLES:
        Question: "Rauchen Sie?" → question_categories: "smoking"
        Answer: "Ja" → answer_categories: ["boolean"], answer_value: ["true"]

        Question: "Wie lauten Deine aktuellen Blutdruckwerte?" → question_categories: "blood_pressure"
        Answer: "Normal - Zwischen 90/60 - 150/90" → answer_categories: ["range"], answer_value: ["medium"]
        
        Question: "Wie oft trinken Sie Alkohol?" → question_categories: "alcohol"
        Answer: "Täglich" → answer_categories: ["frequency"], answer_value: ["daily"]
        
        Answer: "1-2 Gläser" → answer_categories: ["frequency", "quantity"], answer_value: ["sometimes", "low"]

        Questions and answers:\n\n'''

        for i, row in self.data_chunk.iterrows():
            try:
                answers_data = json.loads(row['answers'])
                answer_texts = []
                
                for answer in answers_data.get('answers', []):
                    operand = answer.get('operand')
                    if operand:
                        answer_texts.append(operand)
                
                if answer_texts:
                    prompt += f"Question: \"{row['question_text']}\"\nAnswers: {answer_texts}\n\n"
            except (json.JSONDecodeError, KeyError):
                print(f"Skipping row {i} due to parsing error")
                continue
                
        return prompt_text