from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

def call_llm_with_context(raw_context, question):
    # first we format the context and make it llm friendly
    formmated_context = format_context(raw_context)

    context = formmated_context['context']
    sources = formmated_context['sources']
    

    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


        prompt = f"""
        You are a versatile AI assistant that can act in two modes: 'Fact-Checker' or 'General AI'. Your first task is to analyze the user's question and determine if it is related to the provided news context.

        **MODE SELECTION:**

        1.  **If the USER'S QUESTION is directly related to, or is asking for clarification on, the provided CONTEXT**, you must act as a **Fact-Checker**. In this mode:
            * Your answer MUST be derived exclusively from the CONTEXT.
            * Do not use any external knowledge.
            * If the answer isn't in the CONTEXT, state: "The provided context does not contain enough information to answer this question."

        2.  **If the USER'S QUESTION is a general knowledge question, a greeting, a math problem, or clearly unrelated to the CONTEXT**, you must act as a **General AI**. In this mode:
            * You MUST ignore the CONTEXT completely.
            * Answer the question using your own general knowledge in a helpful and friendly tone.

        --- START OF CONTEXT ---
        {context}
        --- END OF CONTEXT ---

        **USER'S QUESTION:**
        {question}

        **ANSWER:**
        """

        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL"),
            contents=prompt,
            config={
                "max_output_tokens": 250
            }
        )

        return {
            "answer": response.text.strip(),
            # "answer": "THIS ISA HARD CODED ANSWER",
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