import streamlit as st

st.set_page_config(
    page_title="Investment Dashboard",
    page_icon="📊",
)

st.title("Welcome to Markowitz")
st.markdown("Navigate through the sidebar to explore our features.")

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

performance_page = st.Page(
    "pages/performance.py",
    title="Performance",
    icon=":material/insights:",
)


pg = st.navigation(pages=[wel_s, project_1_page, performance_page, about_page])


pg.run()