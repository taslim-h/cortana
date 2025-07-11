# import openai
# from dotenv import load_dotenv
# import os

# load_dotenv()
# text = "Tell me something about taslim?"

# response = openai.embeddings.create(
#     input=text,
#     model="text-embedding-ada-002"
# )

# embeddings = response.data[0].embedding
# print(embeddings)

# import base64
# import json

# with open(r"C:\Users\USER\Downloads\cortana-4cc9a-firebase-adminsdk-fbsvc-2b18bcc557.json") as f:
#     json_data = f.read()



# # encoded = base64.b64encode(json_data.encode()).decode()

# print(json_data)
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# Load environment variables
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "YOUR_PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")

# Initialize embeddings and LLM
embeddings = OpenAIEmbeddings(
    model="text-embedding-ada-002",
    openai_api_key=OPENAI_API_KEY
)
llm = ChatOpenAI(
    model="gpt-3.5-turbo",  # or "gpt-4o" if you have access
    openai_api_key=OPENAI_API_KEY
)

# Initialize Pinecone client and index
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("cortana-meetings")

# Query
query = "taslim"
query_embedding = embeddings.embed_query(query)
result = index.query(vector=query_embedding, top_k=5, include_metadata=True)
print("=== Pinecone Query Result ===")
print(result)

# Gather context from Pinecone results
contexts = []
for match in result['matches']:
    metadata = match.get('metadata', {})
    # Adjust 'text' if your metadata uses a different key
    text = metadata.get('text', '')
    if text:
        contexts.append(text)

context_str = "\n---\n".join(contexts) if contexts else "No relevant documents found."

# Build prompt for LLM
prompt = f"""You are a helpful assistant. Use the following context to answer the question.

Context:
{context_str}

Question: {query}
Answer:"""

# Get answer from LLM
response = llm.invoke(prompt)
print("=== RAG Answer ===")
print(response.content)
print("\n=== Retrieved Contexts ===")
for i, ctx in enumerate(contexts, 1):
    print(f"[{i}] {ctx[:300]}...\n")