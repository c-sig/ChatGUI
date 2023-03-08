import os
import openai
import datetime
import tiktoken
import tkinter as tk
from tkinter import filedialog
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

now = datetime.datetime.now()
day = now.strftime("%A")
time = now.strftime("%I:%M %p")

botname = config.get('settings', 'botname')
immersion = config.get('settings', 'immersion_prompt')
immersion = immersion + f"It's currently {time} on a {day}"
openai.api_key = config.get('settings', 'api_key')
chat_history_text = "working_history.txt"

if not os.path.exists(chat_history_text):
    with open(chat_history_text, 'w') as file:
        pass

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


with open(chat_history_text, "r") as file:
    current_token = str(file.read())

def autosave():
    token_count = (num_tokens_from_string(current_token, "cl100k_base"))
    print(token_count)
    if token_count >= 3072:
        try:
            with open(chat_history_text, 'r') as input_file:
                contents = input_file.readlines()
                num_lines = len(contents)
                midpoint = num_lines // 2
                sliced_contents = contents[:midpoint]
                nowsave = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                output_file_path = f'autosave-{nowsave}.txt'
                with open(output_file_path, 'w') as output_file:
                    output_file.writelines(sliced_contents)
                with open(chat_history_text, 'w') as in_file:
                    in_file.writelines(contents[midpoint:])
                print(f"Autosave successful. Output file path: {output_file_path}")
            input_file.close()
            output_file.close()
        except Exception as e:
            print(f"Error occurred while autosaving: {e}")
        else:
            print("Not enough tokens to trigger autosave")

def save_to_file():
    # Get the contents of the chat history file
    with open('working_history.txt', 'r') as f:
        contents = f.read()

    # Prompt the user to select a file name and location
    file_path = filedialog.asksaveasfilename(
        defaultextension='.txt',
        filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')],
        initialfile='chat_history.txt',
        title='Save Chat History'
    )
    if file_path == '':
        print("User aborted save")
        return
    # Write the contents to the selected file
    with open(file_path, 'w') as f:
        f.write(contents)

def write_message(role, content):
    autosave()
    try:
        with open(chat_history_text, "a") as f:
            f.write(role + ": " + content + "\n")
    except IOError as e:
        print("Error writing message:", e)

def read_message():
    autosave()
    botname = name_window.get('1.0', 'end-1c')
    prompt = prompt_window.get('1.0', 'end-1c')
    prompt = prompt + f"Your name is {botname}"
    prompt = prompt + immersion
    messages = []
    messages.append({"role": "system", "content": prompt})
    try:
        with open(chat_history_text, "r") as f:
            lines = f.readlines()
            for line in lines:
                parts = line.split(": ")
                if len(parts) == 2:
                    role, content = parts
                    messages.append({"role": role, "content": content.rstrip()})
    except IOError as e:
        print("Error reading messages: ", e)
    return messages

def reset():
    enable_type()
    try:
        with open(chat_history_text, "w") as f:
            chat_history.delete('1.0', tk.END)
    except IOError as e:
        print("Error resetting chat history: ", e)
    disable_type()

def get_last_user_response():
    autosave()
    file_path = chat_history_text
    with open(file_path, 'r') as f:
        lines = f.readlines()

    for line in reversed(lines):
        if not line.startswith('user: '):
            return line.strip()
    return None

def regenerate_response():
    autosave()
    enable_type()
    botname = name_window.get('1.0', 'end-1c')
    file_path = chat_history_text
    with open(file_path, 'r') as f:
        lines = f.readlines()

    with open(file_path, 'w') as f:
        f.writelines(lines[:-1])
    chat_history.delete("end-2l", tk.END)
    chat_history.insert(tk.END, '\n')
    user_input = get_last_user_response()
    messages = read_message()
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    reply = response["choices"][0]["message"]["content"]
    write_message("assistant", reply)
    chat_history.insert(tk.END, botname + ": " + reply + "\n")
    chat_history.yview(tk.END)
    disable_type()

def send_message():
    autosave()
    enable_type()
    botname = name_window.get('1.0', 'end-1c')
    try:
        user_input = input_box.get('1.0', 'end-1c')
        write_message("user", user_input)
        messages = read_message()
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        reply = response["choices"][0]["message"]["content"]
        write_message("assistant", reply)
        chat_history.insert(tk.END, "You: " + user_input + "\n")
        chat_history.insert(tk.END, botname + ": " + reply + "\n")
        chat_history.yview(tk.END)
        input_box.delete('1.0', tk.END)
    except openai.error.InvalidRequestError as e:
        print("Invalid request error", e)
    except openai.error.APIConnectionError as e:
        print("API connection error", e)
    except IOError as e:
        print("IO error:", e)
    except Exception as e:
        print("Unexpected error:", e)
    disable_type()

def send_on_enter(event):
    autosave()
    send_message()
    return "break"

def delete_last_two_lines():
    autosave()
    enable_type()
    file_path = chat_history_text
    with open(file_path, 'r') as f:
        lines = f.readlines()

    with open(file_path, 'w') as f:
        f.writelines(lines[:-2])
    chat_history.delete("end-3l", tk.END)
    chat_history.insert(tk.END, '\n')
    disable_type()

def load_current_history():
    autosave()
    enable_type()
    botname = name_window.get('1.0', 'end-1c')
    with open(chat_history_text, 'r') as f:
        for line in f:
            if line.startswith('user:'):
                line = line.replace('user:', 'You:')
            elif line.startswith('assistant:'):
                line = line.replace('assistant:', f'{botname}:')
            chat_history.insert(tk.END, line)
    disable_type()

def enable_type():
    chat_history.config(state=tk.NORMAL)

def disable_type():
    chat_history.config(state=tk.DISABLED)


# GUI Stuff
root = tk.Tk()
root.resizable(False, False)
root.title("Chat")
root.option_add('*Font', ('Inter', 10))

prompt_hint = "Enter your character prompt here."
name_hint = "Enter your character's name here."
input_hint = "Talk to your character here!"

scrollbar = tk.Scrollbar(root)

chat_label = tk.Label(root, text="Chat Window", font=('Inter', 14, 'bold'))
chat_label.grid(row=1, column=1, padx=10, pady=10)

name_window = tk.Text(root, height=2, width=40)
name_window.grid(row=1, column=2, padx=10, pady=10)

chat_history = tk.Text(root, height=20, width=80, yscrollcommand=scrollbar.set, state=tk.DISABLED)
scrollbar.config(command=chat_history.yview)

scrollbar.grid(row=2, column=0, sticky="nse")
chat_history.grid(row=2, column=1, padx=10, pady=10)

prompt_window = tk.Text(root, height=20, width=40)
prompt_window.grid(row=2, column=2, padx=10, pady=10)

input_box = tk.Text(root, height=3, width=80)
input_box.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

prompt_window_scrollbar = tk.Scrollbar(root, command=prompt_window.yview)
prompt_window_scrollbar.grid(row=2, column=3, sticky='nsew')
prompt_window['yscrollcommand'] = prompt_window_scrollbar.set

input_box.insert('1.0', input_hint, 'hint')
input_box.tag_configure('hint', foreground='grey')

prompt_window.insert('1.0', prompt_hint, 'hint')
prompt_window.tag_configure('hint', foreground='grey')

name_window.insert('1.0', name_hint, 'hint')
name_window.tag_configure('hint', foreground='grey')


def show_input_hint(event):
    if input_box.get('1.0', 'end-1c') == input_hint:
        input_box.delete('1.0', 'end')
        input_box.tag_configure('hint', foreground='black')

def hide_input_hint(event):
    if input_box.get('1.0', 'end-1c') == '':
        input_box.insert('1.0', input_hint, 'hint')
        input_box.tag_configure('hint', foreground='grey')

def show_prompt_hint(event):
    if prompt_window.get('1.0', 'end-1c') == prompt_hint:
        prompt_window.delete('1.0', 'end')
        prompt_window.tag_configure('hint', foreground='black')

def hide_prompt_hint(event):
    if prompt_window.get('1.0', 'end-1c') == '':
        prompt_window.insert('1.0', prompt_hint, 'hint')
        prompt_window.tag_configure('hint', foreground='grey')

def show_name_hint(event):
    if name_window.get('1.0', 'end-1c') == name_hint:
        name_window.delete('1.0', 'end')
        name_window.tag_configure('hint', foreground='black')

def hide_name_hint(event):
    if name_window.get('1.0', 'end-1c') == '':
        name_window.insert('1.0', name_hint, 'hint')
        name_window.tag_configure('hint', foreground='grey')

button_frame = tk.Frame(root)
button_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

button_send = tk.Button(button_frame, text="Send", command=send_message)
button_send.pack(side="left", padx=10, pady=10)

button_reset = tk.Button(button_frame, text="Reset", command=reset)
button_reset.pack(side="left", padx=10, pady=10)

button_regen = tk.Button(button_frame, text="Regenerate", command=regenerate_response)
button_regen.pack(side="left", padx=10, pady=10)

button_delete = tk.Button(button_frame, text="Delete Previous", command=delete_last_two_lines)
button_delete.pack(side="left", padx=10, pady=10)

button_save = tk.Button(button_frame, text="Save Chat", command=save_to_file)
button_save.pack(side="left", padx=10, pady=10)

input_box.bind("<Return>", send_on_enter)

load_current_history()

prompt_window.bind('<FocusIn>', show_prompt_hint)
prompt_window.bind('<FocusOut>', hide_prompt_hint)
name_window.bind('<FocusIn>', show_name_hint)
name_window.bind('<FocusOut>', hide_name_hint)
input_box.bind('<FocusIn>', show_input_hint)
input_box.bind('<FocusOut>', hide_input_hint)

root.mainloop()
