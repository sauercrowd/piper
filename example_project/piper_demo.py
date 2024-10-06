from piper.venv_manager import with_venv
import pandas as pd

# using transformers 4.43, which has default_chat_template
with with_venv('./piper_packages/transformers_oldd') as env:
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("facebook/blenderbot-400M-distill")
    print("default_chat_template", tokenizer.default_chat_template)
    df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})

# using transformers 4.44, which no longer has default_chat_template
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("facebook/blenderbot-400M-distill")
print("default_chat_template", tokenizer.default_chat_template)

requests.get("https://www.google.com")
