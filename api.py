import os
import re
import requests
from langchain_community.vectorstores import FAISS
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from fastapi.responses import JSONResponse
from langchain_openai import OpenAIEmbeddings
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredURLLoader

class TrainURLPayload(BaseModel):
    domain:str='https://example.com'
    crawl_mode:str='crawl-all or crawl-single'

class ChatPayload(BaseModel):
    query:str='Hello Chatbot!'

class ChatbotSettingsPayload(BaseModel):
    chat_model_name:str=None
    prompt:str=None
    max_tokens:int=None
    max_temperature:float=None
    INTIAL_MESSAGE:str=None
    WIDGET_BUTTON_URL:str=None
    CHATBOT_DP_URL:str=None
    USER_MESSAGE_COLOR:str=None
    CHATBOT_MESSAGE_COLOR:str=None
    CHATBOT_NAME:str=None

PROMPT = 'You are a helpful assistant!'
MAX_ALLOWED_TEMPERATURE = 0.2
MAX_ALLOWED_TOKENS = 200
BASE_CHAT_MODEL = 'gpt-3.5-turbo'
INTIAL_MESSAGE = "Hello I am Chatbot!"
WIDGET_BUTTON_URL = "chatbot_dp.jpg"
CHATBOT_DP_URL = "chatbot_dp.jpg"
USER_MESSAGE_COLOR = "#ccc"
CHATBOT_MESSAGE_COLOR = "#128b40"
CHATBOT_NAME="Chatbot"

load_dotenv()
backend_key = os.getenv('BACKEND_KEY')

app = FastAPI()
app.title = "Wash Mahdi"
origins = ["http://127.0.0.1:5501"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def validate_api_key(x_author:str):
    if x_author == backend_key:
        return True
    return False

def is_valid_url(url):
    # Define a regular expression pattern for a valid URL with http or https scheme
    url_pattern = re.compile(
        r'^(https?://)(?:(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.)+[A-Za-z]{2,6}$'
    )
    # Check if the provided URL matches the pattern
    if url_pattern.match(url):
        return True
    else:
        return False
        
@app.post("/v1/chatbot/train/url")
async def Train_chatbot_with_url(payload:TrainURLPayload,x_author: str = Header(None)):
    # Validation of API key for the security purpose (You can say it as a password to protect the backend from being exposed)
    if x_author == None:
        return JSONResponse(content={'success':False,'error':'API key is missing'},status_code=401)
    elif not validate_api_key(x_author):
        return JSONResponse(content={'success':False,'error':'Invalid or expired api key!'},status_code=401)
    
    domain = payload.domain
    # Check if the user has passed example domain link.
    if domain == 'https://example.com':
        return JSONResponse(content={'success':False,'error':'You can not use example domain. Please enter real domain.'},status_code=401)
    # Ensure the domain is valid.
    if not is_valid_url(domain):
        return JSONResponse(content={'success':False,'error':f"'{domain}' is not a valid URL. Please ensure it starts with 'http://' or 'https://'."},status_code=400)
    
    persist_directory = 'trained_db/chatbot'
    print("Starting Training for: ",domain)
    # Send a GET request to the website
    response = requests.get(domain)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all the links
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        
        # Convert relative links to absolute links
        base_url = urlparse(domain)
        links = [urljoin(domain, link) for link in links]
        links = list(set(links))
    else:
        print(f"Failed to retrieve content. Status code: {response.status_code}")
        return JSONResponse(content={'error':'Failed while retriving links...'},status_code=400)
    # Parsing Text from All the links extracted above
    if payload.crawl_mode == 'crawl-all':
        documents = UnstructuredURLLoader(urls=links,show_progress_bar=True,continue_on_failure=True).load()
    elif payload.crawl_mode == 'crawl-single':
        documents = UnstructuredURLLoader(urls=[domain],show_progress_bar=True,continue_on_failure=True).load()
    else:
        return JSONResponse(content={'success':False,'error':"Invalid crawl mode please choose either 'crawl-all' or 'crawl-single'"},status_code=500)
    # Chunking large texts to a smaller chunk because we cannot send all the text at once in the prompt.
    # Due to Token Limitation from OpenAI Chat Models
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=20)
    split_docs = text_splitter.split_documents(documents)
    try:
        # Creating Embeddings for Retrived Text 
        embeddings = OpenAIEmbeddings()
        # Storing it VectorDB here I am using FAISS it is best fast and easiest to use for local savings of VectorStore 
        new_vectordb = await FAISS.afrom_documents(split_docs, embeddings)
        new_vectordb.save_local(persist_directory)
        print(len(links))
        return JSONResponse(content={
            'success':True,
            'message':f"Training of '{domain}' was successful!",
            'found_links':links
        },status_code=200)
    except Exception as e:
        return JSONResponse(content={'success':False,'error':str(e)},status_code=500)  
    
@app.post("/v1/chatbot/chat")
async def chat_with_chatbot(payload:ChatPayload,x_author: str = Header(None)):
    # Validation of API key for the security purpose (You can say it as a password to protect the backend from being exposed)
    if x_author == None:
        return JSONResponse(content={'success':False,'error':'API key is missing'},status_code=401)
    elif not validate_api_key(x_author):
        return JSONResponse(content={'success':False,'error':'Invalid or expired api key!'},status_code=401)
    #Setting up the prompt template with 2 varaibes 1. Context , 2. Question
    #Context: In this variable we will pass the relevant context according to the query.
    #Question: Query from the user.
    prompt_template = f'''{PROMPT}\n{{context}}
                        Question: {{question}}
                        Answer:
                        '''
    try:
        embeddings = OpenAIEmbeddings()
        persist_directory = f'trained_db/chatbot'
        #Loading our VectorDatabase
        Vectordb = FAISS.load_local(persist_directory,embeddings)
        #here is where the actual prompt template is intialize.
        _PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        #Intializing our LLM.
        llm = ChatOpenAI(
            temperature=MAX_ALLOWED_TEMPERATURE, 
            model_name=BASE_CHAT_MODEL, 
            max_tokens=MAX_ALLOWED_TOKENS
        )
        #The load_qa_chain function is used to load a question answering chain in LangChain. It is responsible for creating a chain that can be used for question answering. 
        chain = load_qa_chain(llm=llm, chain_type="stuff", prompt=_PROMPT)
        #This is retriver that is responsible for handeling our VectorDB queries.
        retriever = Vectordb.as_retriever(search_type="mmr")
        #We will get relevant documents on the basis of the query.
        docs = retriever.get_relevant_documents(payload.query)
        # print(docs[0].metadata['source'])
        #Will pass that dosuments here. along with the query which will be passed in our PROMPT!
        ans = chain({"input_documents": docs, "question": payload.query})
        answer = ans['output_text']
        #Finally we will return the answer!
        return JSONResponse(content={'success':True,'message':answer},status_code=200)
    except Exception as e:
        return JSONResponse(content={'success':False,'error':f"{str(e)}"},status_code=500)

@app.get("/v1/chatbot/settings")
async def retrive_chatbot_settings(x_author: str = Header(...)):
    # Validation of API key for the security purpose (You can say it as a password to protect the backend from being exposed)
    if x_author == None:
        return JSONResponse(content={'success':False,'error':'API key is missing'},status_code=401)
    elif not validate_api_key(x_author):
        return JSONResponse(content={'success':False,'error':'Invalid or expired api key!'},status_code=401)   
    # Return Current Settings of the Chatbot
    return JSONResponse(
        content={
            'success':True,
            'data':{
                'prompt':PROMPT,
                'max_tokens':MAX_ALLOWED_TOKENS,
                'max_temperature':MAX_ALLOWED_TEMPERATURE,
                'chat_model':BASE_CHAT_MODEL,
                'frontend':{
                    'chatbot_name':CHATBOT_NAME,
                    'initial_message': INTIAL_MESSAGE,
                    'widget_button_url':WIDGET_BUTTON_URL,
                    'chatbot_dp_url':CHATBOT_DP_URL,
                    'user_message_color':USER_MESSAGE_COLOR,
                    'chatbot_message_color':CHATBOT_MESSAGE_COLOR
                }
            }
        },
        status_code=200
    )
@app.put("/v1/chatbot/settings")
async def modify_chatbot_settings(payload:ChatbotSettingsPayload,x_author: str = Header(None)):
    # Validation of API key for the security purpose (You can say it as a password to protect the backend from being exposed)
    if x_author == None:
        return JSONResponse(content={'success':False,'error':'API key is missing'},status_code=401)
    elif not validate_api_key(x_author):
        return JSONResponse(content={'success':False,'error':'Invalid or expired api key!'},status_code=401)
    global PROMPT
    global MAX_ALLOWED_TOKENS
    global MAX_ALLOWED_TEMPERATURE
    global BASE_CHAT_MODEL
    global INTIAL_MESSAGE
    global WIDGET_BUTTON_URL
    global CHATBOT_DP_URL
    global USER_MESSAGE_COLOR
    global CHATBOT_MESSAGE_COLOR
    global CHATBOT_NAME
    # Save new settings...
    if payload.chat_model_name != "string":
        PROMPT = payload.chat_model_name
    if payload.max_tokens != 0:
        MAX_ALLOWED_TOKENS= payload.max_tokens
    if payload.max_temperature != 0:
        MAX_ALLOWED_TEMPERATURE = payload.max_temperature
    if payload.prompt != "string":
        PROMPT = payload.prompt
    if payload.CHATBOT_DP_URL != "string":
        CHATBOT_DP_URL = payload.CHATBOT_DP_URL
    if payload.CHATBOT_MESSAGE_COLOR != "string":
        CHATBOT_MESSAGE_COLOR = payload.CHATBOT_MESSAGE_COLOR
    if payload.CHATBOT_NAME != "string":
        CHATBOT_NAME = payload.CHATBOT_NAME
    if payload.USER_MESSAGE_COLOR != "string":
        USER_MESSAGE_COLOR = payload.USER_MESSAGE_COLOR
    if payload.INTIAL_MESSAGE != "string":
        INTIAL_MESSAGE = payload.INTIAL_MESSAGE
    if payload.WIDGET_BUTTON_URL != "string":
        WIDGET_BUTTON_URL = payload.WIDGET_BUTTON_URL

    return JSONResponse(content={'success':True,'message':'changes saved!'},status_code=200)