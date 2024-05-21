Do a 'universal' app template

Take from bot-lib:
- plugins
- core app

Take from calmlib: 
- beta.app
- examples

Add:
- FastAPI
- FastUI
- Retool
- ??? Electrum + React UI?
- OpenAPI spec tool? 


## Refactoring and cleanup plans

### Idea 1: cleanly extract all the basic plugins

- openai
- langchain
- gpt_engine
- database
- logging
- message_history
- scheduler
- whisper

### Idea 2: start implementing plugins one by one
- add unit tests
- add documentation

