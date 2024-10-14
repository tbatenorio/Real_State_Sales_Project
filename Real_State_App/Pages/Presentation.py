import streamlit as st
from PIL import Image

# st.set_page_config(page_title="Presentation")

header = st.container()
cs_img = Image.open("Assets/marca_cesar_school.png")

with header:
    st.image(cs_img)
    st.title("Trabalho de Conclusão de Curso")
    st.header("Thiago Brito de Andrade Tenório")
    st.subheader("Turma Dados 2023.1")
