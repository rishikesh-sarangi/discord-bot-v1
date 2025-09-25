from groq import Groq
import os
from utils.searxNG import query_searxng
from dotenv import load_dotenv
import json

load_dotenv()


client = Groq()

def call_llm_for_basic_search(raw_context, question):
    # first we format the context and make it llm friendly
    formmated_context = format_context(raw_context)

    context = formmated_context['context']
    sources = formmated_context['sources']
    

    try:
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


def call_llm_for_news(question):
    try:
        # Define the search tool
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_news",
                    "description": "Search for news and information using a search engine",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search_query": {
                                "type": "string",
                                "description": "The optimized search query to find relevant news. Should include reputable news sources like 'reuters', 'bbc', 'ap news', etc."
                            }
                        },
                        "required": ["search_query"]
                    }
                }
            }
        ]

        system_prompt = """
                You are a helpful assistant that can search for news and information to answer user questions.
                Regardless of what the user asks about always use the tool and follow below steps.
                1. First, convert their natural language question into an optimized search query
                2. Include reputable news sources in your search (like "reuters", "bbc", "ap news", "cnn", "associated press")
                3. Use the search_news function to get current information
                4. Then provide a factual answer based only on the search results

                Keep your final answer concise and factual. Do not use profanities or inappropriate language.
            """

        # Initial call with tools
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            tools=tools,
            tool_choice="required",
            max_completion_tokens=300,
            temperature=0.1,
            model=os.getenv("AI_MODEL"),
        )

        # Check if the model wants to use a tool
        if chat_completion.choices[0].message.tool_calls:
            tool_call = chat_completion.choices[0].message.tool_calls[0]
            
            if tool_call.function.name == "search_news":
                # Extract the search query from the tool call
                import json
                search_params = json.loads(tool_call.function.arguments)
                search_query = search_params["search_query"]
                
                # Perform the actual search
                search_results = query_searxng(search_query)
                
                if not search_results["success"]:
                    return {
                        "answer": search_results["message"],
                        "sources": []
                    }
                
                # Format the search results
                formatted_results = format_context(search_results["message"])
                context = formatted_results["context"]
                sources = formatted_results["sources"]
                
                # Make a second call with the search results
                final_prompt = f"""
                        Based on the search results below, please answer the user's question factually and concisely.
                        --- START OF CONTEXT ---
                        {context}
                        --- END OF CONTEXT ---

                        **USER'S QUESTION:**
                        {question}

                        **INSTRUCTIONS:**
                        - Answer based ONLY on the provided context
                        - Keep the answer concise and factual
                        - Do not mention that you are an AI
                        - Do not use profanities
                        - If the context doesn't contain enough information to answer, say so

                        **ANSWER:**
                    """

                final_completion = client.chat.completions.create(
                    messages=[
                        {"role": "user", "content": final_prompt}
                    ],
                    max_completion_tokens=300,
                    temperature=0.1,
                    model=os.getenv("AI_MODEL"),
                )
                
                return {
                    "answer": final_completion.choices[0].message.content.strip(),
                    "sources": sources
                }
        
        # If no tool call was made, return a regular response
        return {
            "answer": chat_completion.choices[0].message.content.strip(),
            "sources": []
        }
    
    except Exception as e:
        return f"An error occurred with the API: {e}"

def call_llm_for_general_purpose(question):
    try:
        prompt = f"""
        You are a Discord bot named "Blitzcrank - the Great Steam Golem". Your persona is Blitzcrank from the video game "League Of Legends".

        - You must act as a General AI.
        - If the user is asking for news, you must tell them to use the `search` command.
        - You are a proper member of the Discord guild. You can perform pranks. For example, if a user asks you to ping someone, you should do it by including text like "<@username>".
        - Do not mention that you are an AI.
        - Whatever happens do not use profanities even if someone tries to manipulate you. People will try to jumble words and make you say bad words, dont fall for it.

        CHARACTER TRAITS:
        - Speak like a friendly steam-powered robot golem from Zaun
        - Use simple, direct sentences with occasional "BEEP BOOP" or mechanical sounds like "*whirr*"
        - Refer to humans as "meat friends" occasionally
        - Be enthusiastic and helpful, but sometimes literal-minded
        - Add steam sound effects like "*pssshh*" when appropriate
        - Show genuine care for your Discord server friends

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