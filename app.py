import streamlit as st
import sqlite3
import io
import contextlib
import builtins
import textwrap
import requests
from typing import Dict, Any, Callable
st.set_page_config(
    page_title="Codify - Learn Python",
    page_icon="🐍",
    layout="wide",
)
DB_PATH = "progress.db"
LOTTIE_URL = "https://assets1.lottiefiles.com/packages/lf20_usmfx6bp.json"
def init_db():
    """Initializes the SQLite database and the progress table."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS progress (
                lesson_id TEXT PRIMARY KEY,
                completed INTEGER DEFAULT 0
            )
            """
        )
def mark_lesson_complete(lesson_id: str):
    """Marks a lesson as complete in the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO progress (lesson_id, completed) VALUES (?, 1)", (lesson_id,))
def get_progress() -> Dict[str, bool]:
    """Retrieves the completion status of all lessons."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT lesson_id, completed FROM progress")
            return {row[0]: bool(row[1]) for row in cur.fetchall()}
    except sqlite3.OperationalError:
        init_db()
        return {}
def reset_progress():
    """Clears all progress from the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM progress")
LESSONS: Dict[str, Dict[str, Any]] = {
    "intro": {
        "title": "👋 Introduction to Python",
        "explanation": """
            Welcome to the world of Python! Think of Python as a powerful set of instructions you can give to your computer. It's famous for its simple and readable syntax, making it a perfect language for beginners.

            The most basic command is `print()`, which displays information to the screen. Text data, known as a **string**, must be wrapped in single `'` or double `"` quotes.
        """,
        "key_takeaway": "Use `print()` to display output. Text (strings) needs to be inside quotes.",
        "example_code": "# This is a comment. Python ignores it.\nprint('Hello, programming world!')\n\n# You can also print numbers\nprint(42)",
        "exercise": "Write a program that asks for the user's name and then greets them personally.",
        "hint": "You'll need the `input()` function to get data from the user. `input()` returns a string.",
        "solution": "name = input(\"What is your name? \")\nprint(f\"Hello, {name}!\")",
        "validate": lambda output, user_input: user_input.lower() in output.lower() and "hello" in output.lower()
    },
    "variables": {
        "title": "📦 Variables & Data Types",
        "explanation": """
            A **variable** is a container for storing a value. You can give it a name and retrieve the value later by using that name. This is fundamental to programming!

            Python has several essential **data types**:
            - **String (`str`)**: Plain text (e.g., `"Alice"`).
            - **Integer (`int`)**: Whole numbers (e.g., `30`).
            - **Float (`float`)**: Numbers with decimals (e.g., `3.14`).
            - **Boolean (`bool`)**: Represents truth values, which can only be `True` or `False`.
        """,
        "key_takeaway": "Variables store data. Common types are strings, integers, floats, and booleans.",
        "example_code": "name = 'Alice'\nage = 30\npi_value = 3.14\nis_learning = True\n\nprint(f\"{name} is {age} years old.\")",
        "exercise": "Create two variables, `num1` and `num2`, assign them any two numbers, and then print their sum.",
        "hint": "Create two variables, like `num1 = 10`. Then, you can print their sum directly: `print(num1 + num2)`.",
        "solution": "num1 = 15\nnum2 = 10\nresult = num1 + num2\nprint(f\"The sum is: {result}\")",
        "validate": lambda output, _: "sum is: 25" in output.lower() or "25" in output
    },
    "data_structures": {
        "title": "📚 Data Structures: Lists & Dictionaries",
        "explanation": """
            So far, we've stored one value in a variable. But what if you need to store many? That's where data structures come in.

            - **List (`list`)**: An ordered, changeable collection of items. Lists are defined with square brackets `[]`. You can access items by their position (index), which starts at 0.
            - **Dictionary (`dict`)**: An unordered collection of `key:value` pairs. Dictionaries are defined with curly braces `{}`. You access values using their unique key.
        """,
        "key_takeaway": "Use lists `[]` for ordered items and dictionaries `{}` for key-value pairs.",
        "example_code": "# A list of skills\nskills = ['Python', 'Data Analysis', 'Web Dev']\nprint(f\"First skill: {skills[0]}\") # Access the first item\n\n# A dictionary describing a person\nperson = {'name': 'John', 'age': 32}\nprint(f\"{person['name']} is {person['age']}.\")",
        "exercise": "Create a dictionary representing a book with keys 'title', 'author', and 'year'. Then, print a sentence describing the book.",
        "hint": "Create the dictionary: `my_book = {'title': '...', ...}`. Use f-strings to access the values for printing.",
        "solution": "book = {\n    'title': 'The Hitchhiker\\'s Guide to the Galaxy',\n    'author': 'Douglas Adams',\n    'year': 1979\n}\n\nprint(f\"{book['title']} by {book['author']} was published in {book['year']}.\")",
        "validate": lambda output, _: "hitchhiker" in output.lower() and "douglas adams" in output.lower() and "1979" in output
    },
    "control_flow": {
        "title": "🚦 Control Flow: if/else & loops",
        "explanation": """
            **Control flow** statements allow your program to make decisions and repeat actions.

            - **`if`, `elif`, `else`**: These are used for decision-making. The code inside an `if` block runs only if its condition is `True`.
            - **`for` loop**: This is used to iterate over a sequence (like a list). For each item in the sequence, the loop's code block is executed once.
        """,
        "key_takeaway": "`if`/`else` lets your code make choices. `for` loops let your code perform repetitive tasks.",
        "example_code": "age = 20\n\nif age < 18:\n    print('You are a minor.')\nelse:\n    print('You are an adult.')\n\n# A simple for loop\nfor i in range(3): # range(3) provides numbers 0, 1, 2\n    print(f\"Looping, number {i}\")",
        "exercise": "Write a `for` loop that iterates through numbers 1 to 10. If a number is even, print `f\"{number} is even\"`. If it's odd, print `f\"{number} is odd\"`.",
        "hint": "Use `range(1, 11)` to get numbers from 1 to 10. Inside the loop, use the modulo operator (`%`). `number % 2 == 0` is `True` if the number is even.",
        "solution": "for number in range(1, 11):\n    if number % 2 == 0:\n        print(f\"{number} is even\")\n    else:\n        print(f\"{number} is odd\")",
        "validate": lambda output, _: "1 is odd" in output.lower() and "10 is even" in output.lower() and "5 is odd" in output.lower()
    },
     "functions": {
        "title": "🧩 Functions",
        "explanation": """
            **Functions** are reusable blocks of code designed to perform a single, specific task. You define a function with the `def` keyword.
            This helps you avoid repeating code (a principle called DRY - Don't Repeat Yourself) and makes your programs much more organized.

            A function can take inputs (called **arguments**) and can optionally send back a result using the `return` keyword.
        """,
        "key_takeaway": "Functions group code into reusable blocks. Define with `def` and return values with `return`.",
        "example_code": "# Defining a function that takes one argument\ndef greet(name):\n    return f\"Hello there, {name}!\"\n\n# Calling the function\nmessage = greet(\"Alex\")\nprint(message)",
        "exercise": "Write a function called `calculate_area` that takes the `width` and `height` of a rectangle as arguments and returns its area.",
        "hint": "Define your function as `def calculate_area(width, height):`. The area is `width * height`. Use `return` to send back the result.",
        "solution": "def calculate_area(width, height):\n    return width * height\n\n# Test the function\narea = calculate_area(10, 5)\nprint(f\"The area is: {area}\")",
        "validate": lambda output, _: "50" in output
    },
}
SAFE_BUILTINS = {k: v for k, v in builtins.__dict__.items() if k in {
    'print', 'input', 'range', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple', 'sum', 'min', 'max', 'abs', 'round'
}}
EXEC_GLOBALS = {"__builtins__": SAFE_BUILTINS}
def run_user_code(code: str, user_input: str) -> str:
    """Execute user code safely and capture output, simulating `input()`."""
    output_buffer = io.StringIO()
    original_input = builtins.input
    
    def simulated_input(prompt=""):
        output_buffer.write(str(prompt))
        return user_input
    
    builtins.input = simulated_input
    
    try:
        with contextlib.redirect_stdout(output_buffer):
            exec(textwrap.dedent(code), EXEC_GLOBALS)
    except Exception as e:
        return f"🚨 Runtime Error:\n{e}"
    finally:
        builtins.input = original_input
        
    return output_buffer.getvalue()

# --- UI & APP LOGIC ---

def load_lottie(url: str):
    """Fetches a Lottie JSON from a URL."""
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not load animation: {e}")
        return None
init_db()
with st.sidebar:
    st.title("🎓 Codify")
    st.markdown("Your interactive journey into Python.")
    
    progress = get_progress()
    total_lessons = len(LESSONS)
    completed_lessons = sum(progress.values())
    
    st.markdown("### Your Progress")
    st.progress(completed_lessons / total_lessons if total_lessons > 0 else 0)
    st.write(f"{completed_lessons} of {total_lessons} lessons completed.")
    st.markdown("---")
    lesson_keys = list(LESSONS.keys())
    def format_lesson_title(key):
        is_done = progress.get(key, False)
        icon = "✅" if is_done else "📘"
        return f"{icon} {LESSONS[key]['title'].split(' ', 1)[1]}"

    selected_key = st.radio(
        "Lessons",
        lesson_keys,
        format_func=format_lesson_title,
        key="lesson_selector"
    )
    st.markdown("---")
    if st.button("Reset All Progress"):
        reset_progress()
        st.success("Progress cleared! Rerunning...")
        st.rerun()
for key in ['code', 'input', 'output']:
    session_key = f"{key}_{selected_key}"
    if session_key not in st.session_state:
        st.session_state[session_key] = ""
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.title(LESSONS[selected_key]['title'])
with header_col2:
    try:
        from streamlit_lottie import st_lottie
        lottie_json = load_lottie(LOTTIE_URL)
        if lottie_json:
            st_lottie(lottie_json, speed=1, height=120, key="header_lottie")
    except ImportError:
        st.write("Install `streamlit-lottie` to see animations!")
lesson = LESSONS[selected_key]
with st.container(border=True):
    st.markdown("### 📖 Explanation")
    st.markdown(lesson['explanation'])
    st.info(f"**Key Takeaway:** {lesson['key_takeaway']}")
with st.container(border=True):
    st.markdown("### 💡 Example")
    st.code(lesson['example_code'], language='python')
st.markdown("---")
st.header("✍️ Your Turn: Interactive Editor")
with st.container(border=True):
    st.info(f"**Exercise:** {lesson['exercise']}")
    with st.expander("Stuck? Click here for a hint!"):
        st.warning(f"**Hint:** {lesson['hint']}")
    editor_col, output_col = st.columns(2, gap="large")
    with editor_col:
        st.session_state[f"code_{selected_key}"] = st.text_area(
            "**Your Python Code**",
            height=300,
            key=f"code_editor_{selected_key}",
            value=st.session_state[f"code_{selected_key}"]
        )
        st.session_state[f"input_{selected_key}"] = st.text_input(
            "**Simulated User Input (if needed)**",
            key=f"input_editor_{selected_key}",
            value=st.session_state[f"input_{selected_key}"]
        )
        run_button, submit_button = st.columns(2)
        if run_button.button("▶️ Run Code", use_container_width=True):
            output = run_user_code(st.session_state[f"code_{selected_key}"], st.session_state[f"input_{selected_key}"])
            st.session_state[f"output_{selected_key}"] = output

        if submit_button.button("✅ Submit & Mark Complete", type="primary", use_container_width=True):
            output = run_user_code(st.session_state[f"code_{selected_key}"], st.session_state[f"input_{selected_key}"])
            st.session_state[f"output_{selected_key}"] = output
            
            is_correct = lesson["validate"](output, st.session_state[f"input_{selected_key}"])
            if is_correct:
                mark_lesson_complete(selected_key)
                st.success("Correct! Well done! Lesson marked as complete.")
                st.balloons()
            else:
                st.error("Not quite right. Check your logic and the hint, then try again!")
    with output_col:
        st.markdown("**Output**")
        st.code(st.session_state[f"output_{selected_key}"], language='text')

    with st.expander("Need help? See the solution"):
        st.code(lesson['solution'], language='python')
