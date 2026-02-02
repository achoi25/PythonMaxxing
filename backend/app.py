import random
import uuid
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

session_store = {}

def gen_int_list(n=10):
    return [random.randint(-10, 50) for _ in range(n)]

def gen_float_list(n=10):
    return [round(random.uniform(-10.0, 50.0), 2) for _ in range(n)]

def gen_word_list(n=10):
    vocab = ["apple", "banana", "cat", "dog", "elephant", "frog", "ghost", "house", "ice", "jungle", "kite", "lemon"]
    return [random.choice(vocab) for _ in range(n)]

def gen_matrix(rows=3, cols=3):
    return [[random.randint(1, 10) for _ in range(cols)] for _ in range(rows)]

def gen_dict(n=5):
    vocab = ["red", "blue", "green", "gold", "silver"]
    return {w: random.randint(1, 100) for w in random.sample(vocab, n)}

SCHEMA = {
    "inputs": {
        "list[int]":   {"var": "nums",  "gen": gen_int_list},
        "list[float]": {"var": "vals",  "gen": gen_float_list},
        "list[str]":   {"var": "words", "gen": gen_word_list},
        "dict":        {"var": "data",  "gen": gen_dict, "iter": ".items()", "unpack": "k, v"},
        "range":       {"var": "i",     "gen": lambda: range(random.randint(5, 15))},
    },
    "outputs": {
        "int": [
            {"expr": "x**2", "desc": "the square of each number"},
            {"expr": "abs(x)", "desc": "the absolute value"},
            {"expr": "x + 10", "desc": "each number plus 10"},
            {"expr": "x * 2", "desc": "double each number"},
            {"expr": "x - 5", "desc": "each number minus 5"},
            {"expr": "x // 2", "desc": "each number divided by 2"},
            {"expr": "-x", "desc": "the negation of each number"},
            {"expr": "x % 10", "desc": "remainder when divided by 10"},
        ],
        "str": [
            {"expr": "len(x)", "desc": "the length of each word"},
            {"expr": "x.upper()", "desc": "the word in uppercase"},
            {"expr": "x[0]", "desc": "the first letter of each word"},
            {"expr": "x.lower()", "desc": "the word in lowercase"},
            {"expr": "x[::-1]", "desc": "each word reversed"},
            {"expr": "x * 2", "desc": "each word repeated twice"},
            {"expr": "x[-1]", "desc": "the last letter of each word"},
        ],
        "dict_item": [
            {"expr": "k", "desc": "the key"},
            {"expr": "v", "desc": "the value"},
            {"expr": "v * 2", "desc": "double the value"},
            {"expr": "len(k)", "desc": "the key length"},
            {"expr": "v // 2", "desc": "the value divided by 2"},
            {"expr": "v + 10", "desc": "the value plus 10"},
        ]
    },
    "filters": {
        "int": [
            {"cond": "x % 2 == 0", "desc": "is even"},
            {"cond": "x > 10", "desc": "is greater than 10"},
            {"cond": "x < 0", "desc": "is negative"},
            {"cond": "x > 0", "desc": "is positive"},
            {"cond": "x % 3 == 0", "desc": "is divisible by 3"},
            {"cond": "x >= 0", "desc": "is non-negative"},
            {"cond": "x <= 0", "desc": "is non-positive"},
            {"cond": "abs(x) > 5", "desc": "absolute value is greater than 5"},
        ],
        "str": [
            {"cond": "len(x) > 4", "desc": "has more than 4 letters"},
            {"cond": "'a' in x", "desc": "contains the letter 'a'"},
            {"cond": "x.startswith('c')", "desc": "starts with 'c'"},
            {"cond": "len(x) < 3", "desc": "has less than 3 letters"},
            {"cond": "x.isupper()", "desc": "is all uppercase"},
            {"cond": "x.islower()", "desc": "is all lowercase"},
            {"cond": "x.endswith('e')", "desc": "ends with 'e'"},
            {"cond": "len(x) == 4", "desc": "has exactly 4 letters"},
        ],
        "dict_item": [
            {"cond": "v % 2 == 0", "desc": "value is even"},
            {"cond": "len(k) > 3", "desc": "key length > 3"},
            {"cond": "v > 50", "desc": "value is greater than 50"},
            {"cond": "v < 20", "desc": "value is less than 20"},
            {"cond": "len(k) == 3", "desc": "key length is exactly 3"},
        ]
    },
    "conditionals": {
        "int": [
            {"expr": "x if x > 0 else 0", "desc": "keep positive numbers, map others to 0"},
            {"expr": "'even' if x % 2 == 0 else 'odd'", "desc": "replace with 'even' or 'odd'"},
            {"expr": "x if x > 0 else -x", "desc": "keep absolute value representation"},
            {"expr": "x * 2 if x > 5 else x", "desc": "double if greater than 5"},
            {"expr": "'pos' if x > 0 else 'neg' if x < 0 else 'zero'", "desc": "positive, negative, or zero label"},
        ],
        "str": [
            {"expr": "x.upper() if len(x) > 4 else x", "desc": "uppercase long words only"},
            {"expr": "len(x) if 'a' in x else -1", "desc": "length if 'a' is present, else -1"},
            {"expr": "x.lower() if x.isupper() else x", "desc": "lowercase if all uppercase"},
            {"expr": "x + 's' if len(x) > 3 else x", "desc": "add 's' if longer than 3 letters"},
        ]
    }
}

class QuestionFactory:
    @staticmethod
    def get_compatible_type(input_key):
        if input_key in ["list[int]", "range", "list[float]"]:
            return "int"
        if input_key == "list[str]":
            return "str"
        if input_key == "dict":
            return "dict_item"
        return "int"

    @staticmethod
    def generate(level):
        input_key = random.choice(list(SCHEMA["inputs"].keys()))
        input_def = SCHEMA["inputs"][input_key]
        op_type = QuestionFactory.get_compatible_type(input_key)

        context = {input_def['var']: input_def['gen']()}
        iter_str = input_def['var']

        iter_var = "x"
        if input_key == "dict":
            iter_str += input_def['iter']
            iter_var = input_def['unpack']

        prompt_text = ""
        code_template = ""
        params = {}

        if level == 1:
            op = random.choice(SCHEMA["outputs"][op_type])
            prompt_text = f"Create a list of {op['desc']} from '{input_def['var']}'"
            code_template = "[{expr} for {iv} in {src}]"
            params = {'expr': op['expr'], 'iv': iter_var, 'src': iter_str}

        elif level == 2:
            filt = random.choice(SCHEMA["filters"][op_type])
            prompt_text = f"Find items in '{input_def['var']}' where {filt['desc']}"
            code_template = "[{iv} for {iv} in {src} if {cond}]"
            params = {'iv': iter_var, 'src': iter_str, 'cond': filt['cond']}

        elif level == 3:
            if input_key == "dict":
                return QuestionFactory.generate(3)
            cond_op = random.choice(SCHEMA["conditionals"][op_type])
            prompt_text = f"From '{input_def['var']}': {cond_op['desc']}"
            code_template = "[{expr} for {iv} in {src}]"
            params = {'expr': cond_op['expr'], 'iv': iter_var, 'src': iter_str}

        elif level == 4:
            context['nums2'] = [1, 2, 3]
            prompt_text = f"Create a list of tuples (x, y) for every x in '{input_def['var']}' and y in 'nums2'"
            code_template = "[(x, y) for x in {src} for y in nums2]"
            params = {'src': iter_str}

        elif level == 5:
            if input_key == "dict":
                return QuestionFactory.generate(5)
            val_op = random.choice(SCHEMA["outputs"][op_type])
            prompt_text = f"Create a dict mapping each item in '{input_def['var']}' to {val_op['desc']}"
            code_template = "{{{iv}: {expr} for {iv} in {src}}}"
            params = {'iv': iter_var, 'expr': val_op['expr'], 'src': iter_str}

        elif level >= 6:
            if input_key == "dict":
                return QuestionFactory.generate(6)
            val_op = random.choice(SCHEMA["outputs"][op_type])
            filt = random.choice(SCHEMA["filters"][op_type])
            prompt_text = f"Dict of items in '{input_def['var']}' mapped to {val_op['desc']}, ONLY IF {filt['desc']}"
            code_template = "{{{iv}: {expr} for {iv} in {src} if {cond}}}"
            params = {'iv': iter_var, 'expr': val_op['expr'], 'src': iter_str, 'cond': filt['cond']}

        target_code = code_template.format(**params)

        try:
            answer = eval(target_code, {}, context)
        except Exception as e:
            return QuestionFactory.generate(1)

        return prompt_text, context, answer

@app.route('/api/question', methods=['GET'])
def get_question():
    level = request.args.get('level', default=None, type=int)
    
    if level is None:
        level = random.choices([1, 2, 3, 4, 5, 6], weights=[1, 2, 2, 1, 2, 2])[0]
    elif level not in range(1, 7):
        return jsonify({"error": "Level must be between 1 and 6"}), 400

    prompt, context, answer = QuestionFactory.generate(level)
    
    context_serializable = {}
    for k, v in context.items():
        if isinstance(v, range):
            context_serializable[k] = list(v)
        else:
            context_serializable[k] = v
    
    question_id = str(uuid.uuid4())
    session_store[question_id] = {
        'answer': answer,
        'context': context
    }
    
    context_display = {}
    for k, v in context.items():
        val_str = str(v)
        if len(val_str) > 60:
            val_str = val_str[:60] + "..."
        context_display[k] = val_str

    return jsonify({
        "id": question_id,
        "level": level,
        "prompt": prompt,
        "context_display": context_display,
        "context": context_serializable,
        "answer": str(answer) if isinstance(answer, range) else answer
    })

@app.route('/api/check', methods=['POST'])
def check_answer():
    data = request.json
    user_code = data.get('code', '')
    question_id = data.get('id')
    
    if not question_id or question_id not in session_store:
        return jsonify({"correct": False, "error": "Question not found"}), 400
    
    question_data = session_store[question_id]
    expected = question_data['answer']
    context = question_data['context']

    try:
        eval_globals = {"__builtins__": __builtins__}
        eval_globals.update(context)
        user_result = eval(user_code, eval_globals)
        
        is_correct = user_result == expected
        return jsonify({
            "correct": is_correct,
            "user_result": str(user_result)[:100],
            "expected": str(expected)[:100]
        })
    except Exception as e:
        return jsonify({
            "correct": False,
            "error": str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=False, port=5000)
