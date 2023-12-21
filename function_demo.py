'''
llama - demonstrates function calling with llama-cpp-python
Based on the sample notebook @ https://github.com/teleprint-me/py.gpt.prompt/blob/main/docs/notebooks/llama_cpp_grammar_api.ipynb and the code snippet
@ https://github.com/abetlen/llama-cpp-python
'''
import json
from llama_cpp import Llama
from duckduckgo_search import DDGS
from halo import Halo
import requests
from typing import *

# https://huggingface.co/abetlen/functionary-7b-v1-GGUF
MODEL_PATH = '/path/to/local/functionary_gguf_file'


@Halo(text='Finding your approximate location', spinner='dots')
def get_location() -> str:
    """
    Geolocate by IP address
    """
    location = list()
    earl = 'http://ipinfo.io/json'
    r = requests.get(earl)
    if r.status_code == 200:
        payload = r.json()
        for key in ('city', 'region', 'country'):
            if key in payload:
                location.append(payload[key])
    if len(location) > 0:
        return ', '.join(location)


@Halo(text='Searching', spinner='dots')
def search_text(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Conducts a search on DuckDuckGo and returns the top max_results results
    """
    results = list()
    with DDGS() as ddgs:
        results = [result for result in ddgs.text(query, max_results=max_results)]
    return results


@Halo(text='Looking for forecasts', spinner='dots')
def get_weather(location: str = None, units: str = None) -> str:
    """
    Searches DuckDuckGo for a forecast. Location defaults to current location based on IP. Units are 'F' or 'C' and defaulting to C.
    """
    if not location:
        location = get_location()
    response = "I'm sorry, I couldn't get the weather for {0}.".format(location)
    if not units:
        units = 'C'
    result = search_text(
        query="What is the current weather forecast for {0} in degrees {1}?".format(location, units),
        max_results=1
    )[0]
    if 'body' in result:
        response = result['body']
        if 'href' in result:
            response += '\n\nSource: {0} '.format(result['href'])
    return response


# Configuration object used to instruct functionary model about the tools at its disposal
TOOL_CONFIG = [
    {
        'type': 'function',
        'function': {
            'name': 'get_weather',
            'description': 'Good for when you want to get the current weather in a given location.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'location': {
                        'type': 'string',
                        'description': 'The geographical location e.g. Minneapolis MN USA or London Ontario Canada.'
                    },
                    'units': {
                        'type': 'string', 
                        'enum': ['F', 'C']
                    }
                },
                'required': []
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'search_text',
            'description': 'Good for when you want to search the web for an answer.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'The search to conduct.'
                    },
                    'max_results': {
                        'type': 'integer', 
                        'description': 'The number of results to return'
                    }
                },
                'required': ['query']
            }
        }
    }
]


# Tool map - when functionary chooses a tool, run the corresponding function from this map
TOOL_MAP = {
    'get_weather': get_weather,
    'search_text': search_text
}


# Initial system instructions passed to the model
FUNCTIONARY_CHAT_INSTRUCTIONS = '''
A chat between a curious user and an artificial intelligence assistant. 
The assistant gives helpful, detailed, and polite answers to the user's questions. 
The assistant calls functions with appropriate input when necessary.
'''


@Halo(text='Formulating response, please stand by', spinner='dots')
def chat(user_input: str):
    """
    Function demo - chooses to run a function based on user input, returns output of the function
    """
    response = "Sorry, I wasn't able to get a good answer for you for that."
    messages = [
        {
            'role': 'system',
            'content': FUNCTIONARY_CHAT_INSTRUCTIONS
        },
        {
            'role': 'user',
            'content': user_input
        }        
    ]
    llm = Llama(
        model_path=MODEL_PATH, 
        n_threads=2,
        chat_format="functionary",
        verbose=False
    )
    function_choices_response = llm.create_chat_completion(messages=messages, temperature=0.2, tools=TOOL_CONFIG)
    if len(function_choices_response) > 0:
        # Find model's first choice for the appropriate function
        first_choice = function_choices_response['choices'][0]
        first_choice_function = first_choice['message'].get('function_call', None)
        if first_choice_function:
            # Find the name of the function from the model's first choice
            function_name = first_choice_function.get('name', None)
            if function_name:
                # Look for the function name in our tool map
                func_to_call = TOOL_MAP.get(function_name, None)
                if func_to_call:
                    # If we found a corresponding tool, look for any arguments the model wants to supply
                    arg_str = first_choice_function.get('arguments', None)
                    if arg_str:
                        # Convert the arguments JSON string to a dict and call the model's choice with the arguments
                        args_to_func = json.loads(arg_str)
                        response = func_to_call(**args_to_func)
    return response


# Sample run - weather for current location
query = "What's the weather in {0}?".format(get_location())
print("Query: '{0}'\n".format(query))
result = chat(user_input=query)
print(result)
print()
