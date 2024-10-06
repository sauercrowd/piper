# piper
piper let's you dynamically switch between different library versions using venvs.

## Example
1. Create a venv with a library version incompatbile with your current environemnt

```bash
python -m venv venv
source venv/bin/activate
pip install transformers=4.43
```

2. Dynamically switch in your code to it
```python
from piper import with_venv

# ... code using your regular transformer version
with with_venv('./venv'):
    import transformers
    # do transfomer 4.43 work

# ... continue with code using your regular transformer version
```
