function_demo
=

![sample output](https://github.com/ccoughlin/functions-llama-cpp-python/blob/main/llama-cpp-python%20functions%20demo.gif)

This is a simple demo of functions with [llama.cpp](https://github.com/ggerganov/llama.cpp) and [llama-cpp-python](https://github.com/abetlen/llama-cpp-python). The model is given a list of tools and asked to choose which function should be used to answer the user's question. If a match is found to the model's selected function, the function is executed and the final answer is the function's output.

In this demo, we ask for the local weather. The model (hopefully) decides that the `get_weather` tool is the most appropriate choice, we search for the weather and return the first result as our final response.

Setup And Installation
--

1. Install the dependencies from `requirements.txt` as usual. 
2. Download a local copy of the [functionary model](https://huggingface.co/abetlen/functionary-7b-v1-GGUF), e.g. 

```bash
huggingface-cli download abetlen/functionary-7b-v1-GGUF functionary-7b-v1.Q4_K_S.gguf --local-dir . --local-dir-use-symlinks False
```

3. Update `MODEL_PATH` in the script to point to the `.gguf` file you downloaded.
4. Want to try other tools / inputs ? Just update the map of tools and the user input accordingly.
