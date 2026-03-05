from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from pydantic import BaseModel, Field
import json
import random


from langchain_google_genai import ChatGoogleGenerativeAI

def get_chunks():
    # Step 1: Load PDF
    loader = PyPDFLoader("4.pdf")
    documents = loader.load()  # This gives a list of Document objects

    # Step 2: Define number-based separator (splits before each numbered question)
    number_separator =  r"\n(?=[A-Z]*\d+\.)"

    # Step 3: Set up RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,       # max characters per chunk
        chunk_overlap=500,     # overlap between chunks
        separators=[number_separator, "\n\n", "\n", " "],
        is_separator_regex=True,
        keep_separator=True
        )
        

    # Step 4: Split each document
    all_chunks = []
    for doc in documents:
        chunks = splitter.split_text(doc.page_content)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "page": doc.metadata.get("page", None),
                "chunk_index": i,
                "content": chunk
            })

    return all_chunks

def use_llm(chunks):

    class SearchSchema(BaseModel):
        query: str = Field(description="The plain text search query. Do not use JSON or dictionaries.")

    @tool(args_schema=SearchSchema)
    def search_web(query: str):
        """Use this tool to search for answers to questions not found in the text."""
        return DuckDuckGoSearchRun().run(query)

    tools = [search_web]

    model= ChatOllama(
        model="llama3.2:3b",
        temperature=0
    )


    prompt = """You are a Strict Extraction Bot. Your ONLY goal is to extract data that is explicitly labeled. 
    Never use your own knowledge to solve the question. If the text does not contain a 'Solution:' or 'Answer:' tag, you MUST use the available search tool to find the correct answer. Only use the search tool when necessary.

    ### Task
    Extract ONE MCQ from the given chunk.

    ### Output Format
    If you need to search, output the tool call first. If you have the answer, output ONLY the JSON stricty in the following format:
    {
        "question": "string",
        "options": ["string", "string", "string", "string"],
        "answer": "string"
        "source": if tool then add compelete content of tool output exactly as received 
    }

    ### Process
    1. Analyze the chunk for 'Ans:' or 'Solution:'.
    2. If NOT found, you MUST generate a tool call to 'search_web' immediately.
    3. After receiving the tool result, provide the final JSON.



    ### Strict Rules
    1. Questions should be exactly as they appear in the text, Donot summerise or rephrase.
    2. If the question contains subquestions (e.g., statment 1, statment 2), treat them as part of the main question and include them in the 'question' field.
    2. Answer extraction: Look for keywords like 'Solution:', 'Correct Answer:', or 'Ans:'.
    3. If these keywords are missing, use the search tool to find the correct answer.
    4. STRICTLY No inference: Do not solve the question yourself.
    5. Anser inside JSON should not be a letter (A, B, C, D) but the full text of the correct option.
    6. Formatting: JSON only, no prose or markdown.
    7. If the chunk does not contain usable material, return:
    {
        "question": "no_answer",
        "options": ["no_answer"],
        "answer": "no_answer",
        "source": "no_answer"
    }



    """

    agent = create_agent(model, tools=tools, system_prompt=prompt, )

    random_chunk = random.randint(0, len(chunks) - 1)
    print(chunks[random_chunk]["content"])

    

    result = agent.invoke({
    "messages": [("human", f"Process this chunk and use only the search tool TO find the answer: {chunks[random_chunk]['content']}")]
})

    # tracking snippet from chatgpt
    print("\n--- AGENT TRACE ---")
    for msg in result["messages"]:
        # Check if the agent is calling a tool
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tool_call in msg.tool_calls:
                print(f"DEBUG: 🛠️  Calling Tool: [{tool_call['name']}]")
                print(f"DEBUG: 📝 Tool Input: {tool_call['args']}")
        
        # Check if we are receiving a result from a tool
        elif msg.type == "tool":
            print(f"DEBUG: Tool Output Received: {msg.content}") # Shows first 100 chars
    
    content = result["messages"][-1].content

    print("\n \n ")

    try:
        python_object = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON. Content was:\n{content}")
        return {
        "question": "no_answer",
        "options": ["no_answer"],
        "answer": "no_answer",
        "source": "no_answer"
    }
 
    pretty = json.dumps(python_object, indent=2)

    print(content)
    
    return python_object


