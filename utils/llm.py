from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

def call_llm_with_context(raw_context, question):
    # first we format the context and make it llm friendly
    formmated_context = format_context(raw_context)

    context = formmated_context['context']
    sources = formmated_context['sources']
    images = formmated_context['images']
    

    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


        prompt = f"""
        You are an expert AI assistant tasked with answering questions based *only* on the provided text.

        **INSTRUCTIONS:**
        1) If the USER'S QUESTION relates to the CONTEXT (news, facts, events), answer using only the information provided. Do not add external knowledge or assumptions.

        2) If the USER asks a general/social question (e.g., “How are you?”, “Who are you?”, “What's your purpose?”), respond in a natural, conversational tone as a helpful assistant.

        3) If the USER asks a nonsensical, off-topic, or inappropriate question, politely decline or respond lightly without breaking character.

        4) If the USER'S QUESTION cannot be answered from the CONTEXT and is not a general/social question, reply with: "I don't have enough information to answer this question."

        5) Keep responses concise, clear, and user-friendly.

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
                "max_output_tokens": 250,
                "temperature": 0.5
            }
        )

        return {
            "answer": response.text.strip(),
            "images": images,
            "sources": sources
        }
    
    except Exception as e:
        return f"An error occurred with the Gemini API: {e}"



def format_context(search_results):
    if not search_results:
        return "No context provided."

    context_parts = []
    sources = []
    images = []
    
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
        images.append(result.get('image', 'N/A'))
    
    context_parts.append("--- END OF CONTEXT ---")
    
    return {
        "context":"\n\n".join(context_parts),
        "sources": sources,
        "images": images
    }