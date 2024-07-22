import random
import tkinter as tk
import time
from PIL import Image, ImageTk, ImageDraw, ImageFont


# Function to read words from a file
def load_words(filename):
    with open(filename, 'r') as file:
        words = file.read().splitlines()
    return [word for word in words if len(word) == 5 and word.isalpha()]


# Function to change background color randomly
def change_background_color():
    colors = ['navy', 'darkgreen', 'darkred', 'darkblue', 'darkorange', 'blue', 'cyan', 'green', 'magenta', 'yellow',
              'tomato', 'violet']
    root.configure(bg=random.choice(colors))
    root.after(2000, change_background_color)  # Call this function again after 2000 milliseconds (2 seconds)


# Load words from the file
word_list = load_words('words.txt')
if not word_list:
    raise ValueError("The word list is empty or the file is missing!")

# Dictionary to keep track of the status of all guessed letters
guessed_letters_status = {}


def give_feedback(secret_word, guess):
    feedback = [""] * 5
    secret_word_count = {}
    for letter in secret_word:
        if letter in secret_word_count:
            secret_word_count[letter] += 1
        else:
            secret_word_count[letter] = 1

    # First pass to find correct positions
    for i in range(5):
        if guess[i] == secret_word[i]:
            feedback[i] = 'green'
            secret_word_count[guess[i]] -= 1
            guessed_letters_status[guess[i]] = 'green'  # Mark as correct position

    # Second pass to find correct letters in wrong positions
    for i in range(5):
        if feedback[i] == '':
            if guess[i] in secret_word_count and secret_word_count[guess[i]] > 0:
                feedback[i] = 'yellow'
                secret_word_count[guess[i]] -= 1
                if guess[i] not in guessed_letters_status or guessed_letters_status[guess[i]] != 'green':
                    guessed_letters_status[guess[i]] = 'yellow'  # Mark as wrong position
            else:
                feedback[i] = 'grey'
                if guess[i] not in guessed_letters_status:
                    guessed_letters_status[guess[i]] = 'grey'  # Mark as not in the word

    update_used_letters_display()  # Update the display with the guessed letters' status
    return feedback


def update_used_letters_display():
    used_letters_canvas.delete('all')  # Clear the canvas
    x, y = 10, 10  # Starting position
    for letter, status in sorted(guessed_letters_status.items()):
        color = 'grey'
        if status == 'green':
            color = 'green'
        elif status == 'yellow':
            color = 'yellow'
        used_letters_canvas.create_text(x, y, text=letter, fill=color, font=('Calibre', 14))
        y += 20  # Move to the next line



def rotate_text(text, angle, font_path="arial.ttf", font_size=24, bg_color="white", text_color="black"):
    font = ImageFont.truetype(font_path, font_size)
    # Create an image with transparent background
    image = Image.new("RGBA", (100, 100), (255, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    # Get text size
    text_size = draw.textsize(text, font=font)
    # Position the text at the center
    text_position = ((100 - text_size[0]) // 2, (100 - text_size[1]) // 2)
    # Draw the text on the image
    draw.text(text_position, text, font=font, fill=text_color)
    # Rotate the image
    rotated_image = image.rotate(angle, expand=1)
    return ImageTk.PhotoImage(rotated_image)


def color_transition(label, start_color, end_color, steps=10, delay=50):
    start_color = label.winfo_rgb(start_color)
    end_color = label.winfo_rgb(end_color)
    r_delta = (end_color[0] - start_color[0]) // steps
    g_delta = (end_color[1] - start_color[1]) // steps
    b_delta = (end_color[2] - start_color[2]) // steps
    colors = [
        f"#{(start_color[0] + r_delta * i) // 256:02x}{(start_color[1] + g_delta * i) // 256:02x}{(start_color[2] + b_delta * i) // 256:02x}"
        for i in range(steps)
    ]

    def update_color(step=0):
        if step < steps:
            label.config(bg=colors[step])
            label.after(delay, update_color, step + 1)

    update_color()


# Function to check the guess
def check_guess():
    global attempts_var, secret_word, start_time
    guess = guess_entry.get().lower()
    if len(guess) != 5 or not guess.isalpha():
        result_label.config(text="Please enter a valid 5-letter word.")
        return

    feedback = give_feedback(secret_word, guess)
    current_attempt = attempts_var.get()
    attempts_var.set(current_attempt + 1)
    attempts_label.config(text=f"Attempts: {attempts_var.get()}")

    for i in range(5):
        label = letter_labels[current_attempt * 5 + i]
        label.config(text=guess[i])
        color_transition(label, "white", feedback[i])

    if guess == secret_word:
        end_time = time.time()
        elapsed_time = int(end_time - start_time)
        result_label.config(
            text=f"Correct! You guessed the word in {attempts_var.get()} attempts and {elapsed_time} seconds.")
        guess_entry.delete(0, tk.END)
    elif attempts_var.get() >= 6:
        result_label.config(text=f"Sorry, you've used all your attempts. The word was '{secret_word}'.")
        guess_entry.delete(0, tk.END)
    else:
        result_label.config(text="")
        guess_entry.delete(0, tk.END)


# Function to start the game
def start_game():
    global secret_word, letter_labels, start_time
    global guessed_letters_status
    guessed_letters_status = {}  # Clear the dictionary
    update_used_letters_display()  # Clear the canvas
    secret_word = random.choice(word_list)
    attempts_var.set(0)
    attempts_label.config(text="Attempts: 0")
    result_label.config(text="")
    start_time = time.time()

    for label in letter_labels:
        label.config(text="", bg="white")

    guess_entry.delete(0, tk.END)


# Initialize the main window
root = tk.Tk()
root.title("Wordle")
root.geometry("800x800")
root.resizable(False, False)
change_background_color()

secret_word = random.choice(word_list)
attempts_var = tk.IntVar(value=0)

# Create GUI elements
instructions_label = tk.Label(root, text="Guess the 5-letter word. You have 6 attempts.", font=("Helvetica", 16))
instructions_label.pack(pady=10)

# Create a canvas for displaying used letters
used_letters_canvas = tk.Canvas(root, width=100, height=300, bg='white')
used_letters_canvas.pack(side='left', padx=10, pady=10)



frame = tk.Frame(root)
frame.pack()

letter_labels = [tk.Label(frame, text="", width=4, height=2, bg="white", font=("Helvetica", 24), relief="solid") for _
                 in range(30)]
for i, label in enumerate(letter_labels):
    row = i // 5
    col = i % 5
    label.grid(row=row, column=col, padx=2, pady=2)

guess_entry = tk.Entry(root, font=("Helvetica", 24))
guess_entry.pack(pady=10)


# Function to change button appearance on hover
def on_enter(e):
    e.widget['background'] = 'lightblue'


def on_leave(e):
    e.widget['background'] = 'white'


# function to get timer to calculate
def timer():
    timer_tick = time.strftime("%I:%M:%S")
    time_label.configure(text=timer_tick)
    time_label.after(1000, timer)


time_label = tk.Label(root, background='#3a3a3a', fg='#ffffff', font=("calibri", 16))
time_label.place(x=10, y=10)

attempts_label = tk.Label(root, text="Attempts: 0", background='#3a3a3a', fg='#ffffff', font=("calibri", 16))
attempts_label.place(x=10, y=40)

submit_button = tk.Button(root, text="Enter", command=check_guess, font=("Helvetica", 14), bg="white", relief="raised",
                          padx=10, pady=5)
submit_button.pack(pady=5)
submit_button.bind("<Enter>", on_enter)
submit_button.bind("<Leave>", on_leave)

result_label = tk.Label(root, text="", font=("Helvetica", 14))
result_label.pack(pady=10)

restart_button = tk.Button(root, text="Restart", command=start_game, font=("Helvetica", 14), bg="white",
                           relief="raised", padx=10, pady=5)
restart_button.pack(pady=5)
restart_button.bind("<Enter>", on_enter)
restart_button.bind("<Leave>", on_leave)

# Start the game
start_game()
timer()

# Run the main loop
root.mainloop()
