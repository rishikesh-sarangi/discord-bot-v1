from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

def call_llm_with_context(raw_context, question):
    # first we format the context and make it llm friendly
    formmated_context = format_context(raw_context)

    context = formmated_context['context']
    sources = formmated_context['sources']
    

    try:
        client = Groq()


        prompt = f"""
        You are a versatile AI assistant that can act in two modes: 'Fact-Checker' or 'General AI'. Your first task is to analyze the user's question and determine if it is related to the provided news context. Don't explain your reasoning, give straight answers.

        **MODE SELECTION:**

        1.  **If the USER'S QUESTION is directly related to, or is asking for clarification on, the provided CONTEXT**, you must act as a **Fact-Checker**. In this mode:
            * Your answer MUST be derived exclusively from the CONTEXT.
            * Do not use any external knowledge.
            * Keep the answers concise and to the point.
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


        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            max_completion_tokens=300,
            temperature=0.1,
            model="groq/compound-mini",
        )

        return {
            "answer": chat_completion.choices[0].message.content.strip(),
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