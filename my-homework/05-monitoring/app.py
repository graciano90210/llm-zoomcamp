import streamlit as st
from assistant import create_assistant

st.title("Course Assistant")

# El asistente se carga una sola vez al iniciar la app
# st.cache_resource evita que se recargue en cada interacción del usuario
@st.cache_resource
def get_assistant():
    return create_assistant()

assistant = get_assistant()

user_input = st.text_input("Enter your question:")

if st.button("Ask"):
    if user_input.strip():
        with st.spinner("Processing..."):
            answer, usage = assistant.rag(user_input)
        st.success("Completed!")
        st.write(answer)
        st.caption(f"Tokens: input={usage.prompt_tokens} | output={usage.completion_tokens}")
    else:
        st.warning("Por favor escribe una pregunta.")
