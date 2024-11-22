import torch
import ollama
import os
from openai import OpenAI
import argparse
import json
import pdfplumber

# ANSI escape codes for colors
PINK = '\033[95m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text


parser = argparse.ArgumentParser(description="LocalRag: Interactive LLM Assistant")
parser.add_argument("--embedding_model", type=str, default="mxbai-embed-large", help="Model used for embeddings")
parser.add_argument("--chat_model", type=str, default="llama3", help="Model used for chat")
args = parser.parse_args()

client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='dolphin-llama3'
)

vault_content = []
if os.path.exists("vault.txt"):
    with open("vault.txt", "r", encoding='utf-8') as vault_file:
        vault_content = vault_file.readlines()

vault_embeddings = []
for content in vault_content:
    try:
        response = ollama.embeddings(model=args.embedding_model, prompt=content)
        vault_embeddings.append(response["embedding"])
    except Exception as e:
        print(CYAN + f"Error generating embeddings for content: {content[:50]}... \nError: {e}" + RESET_COLOR)

vault_embeddings_tensor = torch.tensor(vault_embeddings) if vault_embeddings else torch.empty(0, dtype=torch.float32)


def get_relevant_context(rewritten_input, vault_embeddings_tensor, vault_content, top_k=3):
    if vault_embeddings_tensor.nelement() == 0:
        return []
    try:
        input_embedding = ollama.embeddings(model=args.embedding_model, prompt=rewritten_input)["embedding"]
        cos_scores = torch.cosine_similarity(torch.tensor(input_embedding).unsqueeze(0), vault_embeddings_tensor)
        top_k = min(top_k, len(cos_scores))
        top_indices = torch.topk(cos_scores, k=top_k)[1].tolist()
        return [vault_content[idx].strip() for idx in top_indices]
    except Exception as e:
        print(CYAN + f"Error generating relevant context: {e}" + RESET_COLOR)
        return []


def ollama_chat(user_input, system_message, vault_embeddings_tensor, vault_content, chat_model, conversation_history):
    conversation_history.append({"role": "user", "content": user_input})
    rewritten_query = user_input  # For simplicity, no rewriting for now

    relevant_context = get_relevant_context(rewritten_query, vault_embeddings_tensor, vault_content)
    context_str = "\n".join(relevant_context) if relevant_context else "No relevant context found."
    user_input_with_context = user_input + "\n\nRelevant Context:\n" + context_str

    conversation_history[-1]["content"] = user_input_with_context
    messages = [{"role": "system", "content": system_message}, *conversation_history]

    try:
        response = client.chat.completions.create(
            model=chat_model,
            messages=messages,
            max_tokens=2000
        )
        conversation_history.append({"role": "assistant", "content": response.choices[0].message.content})
        return response.choices[0].message.content
    except Exception as e:
        print(PINK + f"Error during chat completion: {e}" + RESET_COLOR)
        return "Sorry, I couldn't process your query."


pdf_path = 'downloadData/exemple_local.pdf'
pdf_text = extract_text_from_pdf(pdf_path)
print(NEON_GREEN + "PDF Text Extracted: \n\n" + pdf_text + RESET_COLOR)

print("Starting the application...")

conversation_history = []
while True:
    user_input = input(YELLOW + "Ask a query about your documents (or type 'quit' to exit): " + RESET_COLOR)
    if user_input.lower() == 'quit':
        break
    response = ollama_chat(pdf_text, "Your query about the document?", vault_embeddings_tensor, vault_content,
                           args.chat_model, conversation_history)
    print(NEON_GREEN + "Response: \n\n" + response + RESET_COLOR)
