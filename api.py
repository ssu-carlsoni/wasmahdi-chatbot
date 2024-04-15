import os
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from fastapi.responses import JSONResponse
from langchain_openai import OpenAIEmbeddings
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from langchain.chains.question_answering import load_qa_chain

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

PROMPT = "You are eWolf, You're now integrated into the heart of Sonoma University's site. Help our users navigate, find info, and make their journey exceptional. Ready to assist? Just ask how you can make their experience even better! \n Below is some context you can use to assist users:\n"
MAX_ALLOWED_TEMPERATURE = 0.2
MAX_ALLOWED_TOKENS = 200
BASE_CHAT_MODEL = 'gpt-3.5-turbo'
INTIAL_MESSAGE = "🚀 Welcome to eWolf! Your smart guide to all things Sonoma State University. Ask away for info, tips, and more! 🎓✨"
WIDGET_BUTTON_URL = "chatbot_widget.gif"
CHATBOT_DP_URL = "chatbot_dp.png"
USER_MESSAGE_COLOR = "#ccc"
CHATBOT_MESSAGE_COLOR = "#004c97"
CHATBOT_NAME="eWolf"

load_dotenv()
backend_key = os.getenv('BACKEND_KEY')

app = FastAPI()
origins = ["*"] 

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
