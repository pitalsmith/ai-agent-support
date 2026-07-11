from query import retriever

query = "What are the responsibilities of employees?"
docs = retriever.invoke(query)

print(f"--- RETRIEVER TEST ---")
if not docs:
    print("Result: Retriever returned 0 documents.")
else:
    for i, doc in enumerate(docs):
        print(f"\nDocument {i}:")
        print(doc.page_content)
        



        