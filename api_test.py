import requests
import json
import sys

def read_file_in_chunks(file_path, chunk_size):
    """
    Reads a text file in chunks of a specified number of characters.

    Parameters:
    file_path (str): The path to the file.
    chunk_size (int): The number of characters per chunk.

    Yields:
    str: The next chunk of characters from the file.
    """
    try:
        with open(file_path, 'r') as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    except FileNotFoundError:
        print("The file was not found.")
    except IOError:
        print("An error occurred while reading the file.")


system_prompt = """ You are a helpful assistant. Your task is to correct any spelling discrepancies in the transcribed text. Only add necessary punctuation such as periods, commas, and capitalization, and use only the context provided. Do not mention in the response what changes you made or didn't not make. Do not include 'here's the corrected version' or similar phrases in the response. """


# Example usage:
file_path = sys.argv[1]
chunk_size = 2000*4

for chunk in read_file_in_chunks(file_path, chunk_size):


    response = requests.post('http://localhost:11434/api/chat',
              json={"model" : "llama3",
                    "stream" : False,
                    "messages" : [
                        {
                        "role" : "system",
                        "content" : system_prompt
                        
                        },
                    {
                        "role" : "user",
                       "content": chunk 
                        }
                    ]
                    })

    data = json.loads(response.text)['message']['content']
    print('===================== RESPONSE ========================')
    print(data)
