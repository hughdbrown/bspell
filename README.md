# Description
A simple spell checking app in python.

# Installation
This part is a bit rough. These parts should be automated but they are not.

```
pyenv virtualenv 3.12.0 bspell-3.12.0
pyenv local bspell-3.12.0
pip install -r requirements.txt
```

# Usage
1. Traverse to a directory
2. Invoke the application from the command line
```
$ ./bspell.py
```

You will be prompted for actions to apply to misspelled words it finds (i.e. words not in its dictionary). Possible responses are:
1. y: Replace the misspelled word

You will be prompted for the change.

2. n: Do not replace the misspelled word

3. a: Add the misspelled word to the in-memory dictionary

Unfortunately, this is only temporary.

4. s: Do not check any more words in the file

# Dictionary
The dictionary is taken from the standard location on a Mac. If that is no good for you, override the location and file name with the command line option.

# Help
```
Usage: bspell.py [OPTIONS]

  Traverse down directory tree, opening all files, looking for words that do
  not appear in the dictionary.

Options:
  -d, --dict_filename TEXT
  --help                    Show this message and exit.
```
