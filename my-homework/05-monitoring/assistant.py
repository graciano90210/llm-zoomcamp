import os
import time
from dotenv import load_dotenv
from groq import Groq
import requests
from minsearch import Index
import psycopg

load_dotenv()

MODEL = "llama-3.3-70b-versatile"

INSTRUCTIONS = """
Your task is to answer questions from the course participants
based on the provided context.

Use the context to find relevant information and provide accurate
answers. If the answer is not found in the context,
respond with "I don't know."
""".strip()

PROMPT_TEMPLATE = """
QUESTION: {question}

CONTEXT:
{context}
""".strip()


def get_db_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        dbname=os.getenv("POSTGRES_DB", "course_assistant"),
        user=os.getenv("POSTGRES_USER", "user"),
        password=os.getenv("POSTGRES_PASSWORD", "password"),
    )


def save_span(span_name, duration, input_tokens=None, output_tokens=None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO spans (span_name, duration, input_tokens, output_tokens)
                VALUES (%s, %s, %s, %s)
                """,
                (span_name, duration, input_tokens, output_tokens),
            )
        conn.commit()
    finally:
        conn.close()


def load_faq_data():
    docs_url = "https://datatalks.club/faq/json/courses.json"
    courses_raw = requests.get(docs_url).json()
    documents = []
    url_prefix = "https://datatalks.club/faq"
    for course in courses_raw:
        course_url = f"{url_prefix}{course['path']}"
        course_data = requests.get(course_url).json()
        documents.extend(course_data)
    for doc in documents:
        doc["doc_id"] = doc.pop("id")
    return documents


def build_index(documents):
    index = Index(
        text_fields=["question", "section", "answer"],
        keyword_fields=["course"],
    )
    index.fit(documents)
    return index


class Assistant:
    def __init__(self, index):
        self.index = index
        self.client = Groq(api_key=os.environ["GROQ_API_KEY"])

    def search(self, query):
        return self.index.search(
            query,
            num_results=5,
            boost_dict={"question": 3.0, "section": 0.5},
            filter_dict={"course": "llm-zoomcamp"},
        )

    def build_prompt(self, query, results):
        lines = []
        for doc in results:
            lines.append(doc["section"])
            lines.append("Q: " + doc["question"])
            lines.append("A: " + doc["answer"])
            lines.append("")
        context = "\n".join(lines).strip()
        return PROMPT_TEMPLATE.format(question=query, context=context)

    def llm(self, prompt):
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": INSTRUCTIONS},
                {"role": "user", "content": prompt},
            ],
        )
        answer = response.choices[0].message.content
        usage = response.usage
        return answer, usage

    def rag(self, query):
        t0 = time.time()

        t1 = time.time()
        results = self.search(query)
        save_span("search", time.time() - t1)

        prompt = self.build_prompt(query, results)

        t2 = time.time()
        answer, usage = self.llm(prompt)
        save_span("llm", time.time() - t2,
                  input_tokens=usage.prompt_tokens,
                  output_tokens=usage.completion_tokens)

        save_span("rag", time.time() - t0)

        return answer, usage


def create_assistant():
    print("Cargando FAQ...")
    documents = load_faq_data()
    index = build_index(documents)
    print(f"Índice listo: {len(documents)} documentos")
    return Assistant(index)


if __name__ == "__main__":
    import sys
    assistant = create_assistant()
    query = sys.argv[1] if len(sys.argv) > 1 else "How do I join the course?"
    answer, usage = assistant.rag(query)
    print("\n--- Respuesta ---")
    print(answer)
    print(f"\nTokens: input={usage.prompt_tokens}, output={usage.completion_tokens}")
