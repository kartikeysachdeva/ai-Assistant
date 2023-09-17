ASTRA_DB_SECURE_BUNDLE_PATH = "/Users/kartisa/Library/CloudStorage/OneDrive-UniversityofToronto/PJ/search-python/secure-connect-vector-database.zip"
ASTRA_DB_APPLICATION_TOKEN = "AstraCS:WqrYWquZHmyBweiOmbphbekW:7f8c681b5bfd6896cb63293db9039e4ea63536b3441aeff46cba899af5bd9aa1"
ASTRA_DB_CLIENT_ID = "WqrYWquZHmyBweiOmbphbekW"
ASTRA_DB_CLIENT_SECRET = "-lTlsCqa+92Z55wm0iYZael,E.3qdB-CtCSx,Z_TDwK-dfTwedoE8djxvyxTcgt1.i2MueOkcR3uXOn,L1pE3wDQnTA_JmA6rzH-CnjRO6gHgk7n1C0OU475.da,L8e3"
ASTRA_DB_KEYSPACE = "search"
OPENAI_API_KEY = "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"

from langchain.vectorstores.cassandra import Cassandra
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
#importing as llm
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

from datasets import load_dataset

cloud_config= {
    'secure_connect_bundle' : ASTRA_DB_SECURE_BUNDLE_PATH
}

auth_provider = PlainTextAuthProvider(ASTRA_DB_CLIENT_ID, ASTRA_DB_CLIENT_SECRET)
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
astraSession = cluster.connect()


llm = OpenAI(openai_api_key=OPENAI_API_KEY)
myEmbedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

myCassandraVStore = Cassandra(
    embedding=myEmbedding,
    session=astraSession,
    keyspace=ASTRA_DB_KEYSPACE,
    table_name="qa_mini_demo"
)

vectorIndex = VectorStoreIndexWrapper(vectorstore=myCassandraVStore)

first_question = True 
while True:
    if first_question:
        query_text = input("\nEnter your question ")
        first_question = False
    else:
        query_text = input("Enter another question (or enter q to quit):")
    
    if query_text.lower() == 'quit':
        break

    print("QUESTION: \"%s\"" % query_text)
    answer = vectorIndex.query(query_text, llm = llm).strip()
    print("ANSWER: \"%s\"\n" % answer)

    print("DOCUMENTS BY RELEVANCE:")
    for doc, score in myCassandraVStore.similarity_search_with_score(query_text, k =4):
        print("  %0.4f \"%s ...\"" % (score, doc.page_content[:60]))

print("Loading data from huggingface")
myDataset = load_dataset("Biddls/Onions_News", split="train")
headlines = myDataset["text"][:50]

print("\nGenerating embeddings and storing in AstraDB")
myCassandraVStore.add_texts(headlines)

print("Inserted %i headlines. \n" % len(headlines))




















































































#https://www.youtube.com/watch?v=yfHHvmaMkcA&t=703s
