import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def call_llm_with_context(raw_context, question):
    # first we format the context and make it llm friendly
    formmated_context = format_context(raw_context)

    context = formmated_context['context']
    sources = formmated_context['sources']
    

    try:
        # genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        # model = genai.GenerativeModel(os.getenv("GEMINI_MODEL"))

        # prompt = f"""
        # You are an expert AI assistant tasked with answering questions based *only* on the provided text.

        # **INSTRUCTIONS:**
        # 1.  Read the CONTEXT below carefully.
        # 2.  Your answer must be derived exclusively from the information within the CONTEXT.
        # 3.  Do not use any external knowledge or make assumptions.
        # 4.  Answer the USER'S QUESTION concisely.
        # 5.  If the answer cannot be found in the CONTEXT, you must state: "The provided context does not contain enough information to answer this question."

        # --- START OF CONTEXT ---
        # {context}
        # --- END OF CONTEXT ---

        # **USER'S QUESTION:**
        # {question}

        # **ANSWER:**
        # """

        # generation_config = genai.types.GenerationConfig(max_output_tokens=250)

        # response = model.generate_content(prompt, generation_config=generation_config) 
    
        return {
            # "answer": response.text.strip(),
            "answer": "THIS ISA HARD CODED ANSWER",
            "sources": sources
        }
    
    except Exception as e:
        return f"An error occurred with the Gemini API: {e}"



def format_context(search_results):
    if not search_results:
        return "No context provided."

    context_parts = []
    sources = []
    
    context_parts.append("--- CONTEXT FROM SEARCH RESULTS ---")

    for i, result in enumerate(search_results, 1):
        formatted_item = (
            f"Source [{i}]:\n"
            f"  Title: {result.get('title', 'N/A')}\n"
            f"  Link: {result.get('link', 'N/A')}\n"
            f"  Snippet: {result.get('snippet', 'N/A')}\n"
        )
        context_parts.append(formatted_item)

        sources.append(result.get('link', 'N/A'))
    
    context_parts.append("--- END OF CONTEXT ---")
    
    return {
        "context":"\n\n".join(context_parts),
        "sources": sources
    }