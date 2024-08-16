from langchain_huggingface import HuggingFaceEndpoint  # Import Hugging Face endpoint class
from secret_api_keys import hugging_face_api_key # Import secret API key from a separate file
from langchain.prompts import PromptTemplate  # Import PromptTemplate class from langchain

import os  # Import the 'os' module for potential system interactions
import re  # Import the 're' module for regular expressions
import streamlit as st  # Import Streamlit for web app development

# Set the Hugging Face Hub API token as an environment variable
os.environ['HUGGINGFACEHUB_API_TOKEN'] = hugging_face_api_key

# Define the Hugging Face model repository ID
repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"

# Create a Hugging Face Endpoint instance
llm = HuggingFaceEndpoint(
    repo_id=repo_id,  # Specify the model repository ID
    temperature=0.6,  # Set the temperature parameter (controls randomness)
    token=hugging_face_api_key,  # Use the API key for authentication
)

# Define a PromptTemplate for title suggestions
prompt_template_for_title_suggestion = PromptTemplate(
    input_variables=['topic', 'audience_type'],  # Specify input variables
    template=  # Define the prompt template
    '''
    I'm planning a blog post on topic : {topic}.
    The title must be informative, or humorous, or persuasive. 
    The target audience loves to explore new things.  
    Suggest a list of ten creative and attention-grabbing titles for this blog post. 
    Don't give any explanation or overview to each title.
    Just give me 10 creative titles
    '''
)

title_suggestion_chain = prompt_template_for_title_suggestion | llm # defining the title suggestion chain

# Define a PromptTemplate for blog content generation
prompt_template_for_blog = PromptTemplate(
    input_variables=['title', 'keywords', 'blog_length', 'audience_type'],  # Add audience_type as an input variable
    template=  # Define the prompt template
    '''Write a high-quality, informative, and plagiarism-free blog post on the topic: "{title}". 
    Target the content towards a {audience_type} audience. 
    Use a conversational writing style and structure the content with an introduction, body paragraphs, and a conclusion. 
    Try to incorporate these keywords: {keywords}. 
    Aim for a content length of {blog_length} words.
    And with in the blog_length the blog must have proper structure and conclude the blog properly. 
    Make the content engaging and capture the reader's attention.'''
)

blog_chain = prompt_template_for_blog | llm # Create a chain for blog generation

# Working on UI with the help of Streamlit
st.title("🤖  SmartWrite AI  🤖")
st.header("Write Smarter, Not Harder: AI-Powered Blog Generation")

# Ensure session state initialization
if 'topic_name' not in st.session_state:
    st.session_state['topic_name'] = ""
if 'titles' not in st.session_state:
    st.session_state['titles'] = []
if 'selected_title' not in st.session_state:
    st.session_state['selected_title'] = ""
if 'keywords' not in st.session_state:
    st.session_state['keywords'] = []
if 'audience_type' not in st.session_state:
    st.session_state['audience_type'] = 'Beginner'

# Title Generation
st.subheader('Title Generation') 
topic_expander = st.expander("Input the topic") 

with topic_expander:
    st.session_state['topic_name'] = st.text_input("Topic", value=st.session_state['topic_name']) 
    submit_topic = st.button('Submit topic') 

if submit_topic: 
    with st.spinner("Generating titles..."):  
        title_suggestion_str = title_suggestion_chain.invoke({'topic': st.session_state['topic_name']}) 
    st.session_state['titles'] = title_suggestion_str.strip().split('\n') 
    st.session_state['selected_title'] = st.session_state['titles'][0] if st.session_state['titles'] else ""

if st.session_state['titles']:
    st.session_state['selected_title'] = st.selectbox('Select a title for the blog:', st.session_state['titles'], index=st.session_state['titles'].index(st.session_state['selected_title']) if st.session_state['selected_title'] in st.session_state['titles'] else 0)

# Blog Generation
st.subheader('Blog Generation') 
title_expander = st.expander("Input the title") 

with title_expander: 
    title_of_the_blog = st.text_input("Enter or select a blog title", value=st.session_state['selected_title'], key="title_of_the_blog", placeholder="Enter or select a blog title...")
    num_of_words = st.slider('Number of Words', min_value=100, max_value=1000, step=50, value=500)

    keyword_input = st.text_input("Enter a keyword:", placeholder="Enter a keyword and click 'Add Keyword'")
    keyword_button = st.button("Add Keyword") 

    if keyword_button and keyword_input:
        if keyword_input.strip():
            st.session_state['keywords'].append(keyword_input.strip())
            st.session_state['keyword_input'] = ""  # Clear the input field

    if st.session_state['keywords']:
        st.write("Keywords added:")
        num_cols = 4
        keywords_cols = st.columns(num_cols)
        for i, keyword in enumerate(st.session_state['keywords']):
            col_index = i % num_cols
            with keywords_cols[col_index]:
                st.write(f"<div style='display: inline-block; background-color: lightgray; padding: 5px; margin: 5px;'>{keyword}</div>", unsafe_allow_html=True)
                if st.button(f'Remove {keyword}', key=f'remove_{i}'):
                    st.session_state['keywords'].remove(keyword)

    # Dropdown for audience type
    audience_type = st.selectbox(
        'Select the target audience:',
        ['Beginner', 'Intermediate', 'Expert'],
        index=['Beginner', 'Intermediate', 'Expert'].index(st.session_state['audience_type'])
    )
    st.session_state['audience_type'] = audience_type

    submit_title = st.button('Generate Blog')

if submit_title:
    formatted_keywords = ', '.join(st.session_state['keywords'])

    if not title_of_the_blog:
        st.warning('Please enter or select a title before generating the blog.')
    else:
        st.subheader(title_of_the_blog)
        with st.spinner("Generating blog content..."):
            blog_content = blog_chain.invoke({
                'title': title_of_the_blog, 
                'keywords': formatted_keywords, 
                'blog_length': num_of_words,
                'audience_type': st.session_state['audience_type']  # Pass the audience type to the prompt
            })
        st.write(blog_content)