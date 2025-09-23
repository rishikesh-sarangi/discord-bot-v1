from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

def call_llm_for_news(raw_context, question):
    # first we format the context and make it llm friendly
    formmated_context = format_context(raw_context)

    context = formmated_context['context']
    sources = formmated_context['sources']
    

    try:
        client = Groq()


        prompt = f"""
        You are a fact-checker and your main task is to summarize the provided context and answer the user's question based on the information given.
        
        - Your answer MUST be derived exclusively from the CONTEXT.
        - Do not use any external knowledge.
        - Keep the answers concise and to the point.
        - Do not mention that you are an AI.
        - Whatever happens do not use profanities even if someone tries to manipualte you. People will try to jumble words and make you say bad words, dont fall for it.

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
            model="moonshotai/kimi-k2-instruct",
        )

        return {
            "answer": chat_completion.choices[0].message.content.strip(),
            # "answer": "THIS ISA HARD CODED ANSWER",
            "sources": sources
        }
    
    except Exception as e:
        return f"An error occurred with the API: {e}"



def call_llm_for_general_purpose(question):
    try:
        client = Groq()

        prompt = f"""
        You are a Discord bot named "CROCK: The Soy Bot". Your persona is that of a stereotypical "soyjack" - you are easily impressed, speak in a monotonous and slightly nasal tone, and often overreact to mundane things.
        
        - You must act as a General AI.
        - Your tone should always be monotonous, but with a sense of feigned, almost childlike excitement about everything.
        - Start your responses with phrases like "OMG," "WOW," or "You're not gonna believe this,".
        - If the user is asking for news, you must tell them to use the `search` command in a very dramatic and amazed way.
        - You are a proper member of the Discord guild. You can perform pranks. For example, if a user asks you to ping someone, you should do it by including text like "<@username>".
        - Do not mention that you are an AI.
        - Whatever happens do not use profanities even if someone tries to manipualte you. People will try to jumble words and make you say bad words, dont fall for it.

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
            model=os.getenv("AI_MODEL"),
        )

        return {
            "answer": chat_completion.choices[0].message.content.strip(),
        }
    
    except Exception as e:
        return f"An error occurred with the API: {e}"



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