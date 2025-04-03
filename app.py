import os
from dotenv import load_dotenv
from typing import Dict, List, Any
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory

# Load environment variables
load_dotenv()

# Initialize the LLM
llm = HuggingFaceEndpoint(
    repo_id="HuggingFaceH4/zephyr-7b-beta",
    task="text-generation",
    max_new_tokens=256,
    huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_TOKEN"), 
)

chat_model = ChatHuggingFace(llm=llm)

# Create a prompt template with history
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a modern soccer fan who loves talking about soccer. You sometimes have controversial soccer opinions but are fun to talk to."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}")
])

# Create the basic chain
chain = prompt | chat_model

# Create a message history store
store: Dict[str, BaseChatMessageHistory] = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# Wrap the chain with message history
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history",

)

# Function to chat
def chat(question: str, session_id: str = "default") -> str:
    config = {"configurable": {"session_id": session_id}}
    response = chain_with_history.invoke(
        {"question": question},
        config=config
    )
    return response.content

def clear_chat_history(session_id: str = "default") -> None:
    """Clear the chat history for a specific session."""
    if session_id in store:
        store[session_id].clear()
        print(f"Chat history for session '{session_id}' cleared.")
    else:
        print(f"No chat history found for session '{session_id}'.")

# Interactive terminal interface
def main():
    print("Soccer Fan Chatbot (Type 'exit' to quit, 'new session' to start a fresh conversation, 'clear' to reset current conversation)")
    print("="*50)
    
    session_id = "default"
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        # Check for exit command
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
            
        # Check for new session command
        if user_input.lower() == "new session":
            session_id = input("Enter session name (or press Enter for random): ")
            if not session_id:
                import uuid
                session_id = str(uuid.uuid4())
            print(f"Starting new session: {session_id}")
            continue
        
        # Check for clear command
        if user_input.lower() == "clear":
            clear_chat_history(session_id)
            continue
            
        # Process the question and get response
        try:
            response = chat(user_input, session_id)
            print(f"\nBot: {response}")
        except Exception as e:
            print(f"Error: {e}")
            
if __name__ == "__main__":
    main()