# ChatGUI
## A Simple GUI to Interact with OpenAI Models

### Disclaimer
**Please refrain from using this program to break OpenAI Terms of Service!**

### Requirements
**Python 3.9**

### Usage
**0. Download the repository through git or by downloading the .zip file**
> git clone https://github.com/c-sig/ChatGUI.git

**1. Install requirements by opening a terminal in the root folder**
> pip install -r requirements.txt

**2. Put your OpenAI API key in config.ini**
> api_key = Your key here

**2.1 Replace botname with your own value (optional)**
> botname = Name

**2.2 Adapt immersion prompt to your needs (optional)**
> immersion_prompt = prompt preventing ChatGPT from acting out

**3. Launch GUI by opening a terminal in the root folder again**
> python main.py



## Guide
**SEND** - Sends your message. Pressing [ENTER] on your keyboard also sends your message.

**RESET** - Clears your chat history.

**REGENERATE** - Deletes previous bot message and regenerates a reply.

**DELETE PREVIOUS** - Deletes previous user and bot message from chat history.

**SAVE CHAT** - Option to save chat history with a custom name. Keep in mind that application can only read chat history if the file is named "working_history.txt"


**PROMPT CREATION**
One way to generate character prompts would be to ask ChatGPT to "pretend they're the character". After they introduce themseves, ask ChatGPT to replace all personal pronouns with "you". Use this to help create your character.
