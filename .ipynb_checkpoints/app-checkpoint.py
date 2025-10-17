import streamlit as st

project_1_page = st.Page(
    "pages/main.py",
    title="Portfolio",
    icon=":material/bar_chart:",
    
    )

about_page = st.Page(
    "pages/about.py",
    title="About",
    icon=":material/account_circle:",
    
)
wel_s = st.Page(
    "pages/wel.py",
    title="welcom",
    icon=":material/account_circle:",
    default=True,
)

pg = st.navigation(pages=[wel_s, project_1_page , about_page])

pg.run()