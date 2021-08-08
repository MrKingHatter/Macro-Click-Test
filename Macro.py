import pynput
import time
import os
import pyscreenshot
from PIL import Image


class Mouse:
    """
    Mouse object to handle the pynput mouse
    Attributes:
        mouse: pynput mouse controller object
    Methods:
        click: method for simulating a mouse click
        move: method for moving the cursor to a position
    """
    def __init__(self):
        self.mouse = pynput.mouse.Controller()  # Initiate the mouse controller

    def click(self, button, x, y):
        """
        Simulates a mouse click
        Arguments:
            button: the button to be clicked
            x: the x position of the click on the screen
            y: the y position of the click on the screen
        """
        self.move((x, y))           # Move the cursor to position (x, y)
        self.mouse.click(button)    # Simulate a mouse click

    def move(self, pos):
        """
        Moves the mouse to a position
        Arguments:
            pos: a tuple describing where to move the cursor (x, y)
        """
        x0, y0 = self.mouse.position    # Get current position of the cursor
        x, y = pos                      # Get the wanted position of the cursor
        self.mouse.move(x-x0, y-y0)     # Move the cursor to the wanted position


class Keyboard:
    """
    Keyboard object to handle the pynput keyboard
    Attributes:
        keyboard: a pynput keyboard controller object
    Methods:
        key_press: method for pressing a key
        key_release: method for releasing a key
    """
    def __init__(self):
        self.keyboard = pynput.keyboard.Controller()    # Initiate the keyboard controller

    def key_press(self, key):
        """
        Method for simulating a key press
        Arguments:
             key: the key to be press
        """
        self.keyboard.press(key)    # Press the given key

    def key_release(self, key):
        """
        Method for simulating a key press
        Arguments:
        key: the key to be press
        """
        self.keyboard.release(key)  # Release the given key


class Document:
    """
    A Document object for handling the macro script txt
    Attributes:
        address: the file address of the macro script
        document: a list of strings containing timestamps and orders
    Methods:
        save: a method for saving the document to the address
        read: a method for reading the address into the document
        append: a method for adding a new order to the document
    """
    def __init__(self, address, read=False):
        self.address = address  # Set the address
        self.document = []      # Initialize the document
        if read:
            self.read()         # Read the address to the document if read

    def save(self):
        """
        Method for saving the document to the given address
        """
        with open(self.address + '\\macro.txt', 'w+') as file:  # Open the address
            file.writelines(self.document)      # Write the document to the address

    def read(self):
        """
        Method for reading the file at the address into the document list
        """
        # Read the document as a string and split it into a list
        self.document = open(self.address + '\\macro.txt').read().split('\n')

    def append(self, string: str):
        """
        Method for appending a string to the document
        Arguments:
            string: the string to append to the document
        """
        self.document.append(string + '\n')     # Append the string to the document list along with a newline character


class Timer:
    """
    A Timer object to count time since the start method was called
    Attributes:
        base_time: the time the start method last was called
    Method:
        start: a method for setting the base_time to the current time
        check: a method that returns the times since the start method was called
    """
    def __init__(self):
        self.base_time = 0  # Initialize the base_time
        self.start()        # Set the base_time

    def start(self):
        """
        Resets the base_time to the current time that has passed since script start
        """
        self.base_time = time.perf_counter()    # Set the base_time to the current time

    def check(self) -> float:
        """
        Checks the time that has passed since start was called
        Returns:
            float that describes the amount of seconds since start was called
        """
        return time.perf_counter() - self.base_time     # Return the time that has passed


class Screen:
    """
    Screen object for handling screenshots
    Attributes:
        box: the bounding box for the screenshots
        counter: a counter for comparing between the right screenshots
        bool: a bool describing if the current screen is correct
    Methods:
        get_box: creates a bounding box from user clicks
        save_box: save the box corners to at txt document
        read_box: read a bounding box from a txt document
        screenshot_save: takes and saves a screenshot in the bounding box
        screenshot_compare: takes a screenshot and compares to a saved screenshot
    """
    def __init__(self):
        self.box = []       # Initialize the bounding box
        self.counter = 1    # Initialize the screenshot counter
        self.bool = True    # Initialize the comparison boolean

    def get_box(self):
        """
        Creates a bounding box by letting the user click in the corners
        """
        # Defines click behavior to save the cursor position to the box
        def on_click(x, y, button, pressed):
            if pressed:
                self.box.append((x, y))
                if len(self.box) == 1:
                    print('Please click the bottom right corner of the window')

        self.box = []                                           # Empty the bounding box
        listener = pynput.mouse.Listener(on_click=on_click)     # Initialize a mouse listener
        listener.start()                                        # Start the listener
        print('Please click the top left corner of the window')
        while len(self.box) < 2:                                # Loop until two corners defined
            pass
        listener.stop()                                         # Stop the listener

    def save_box(self, address):
        """
        Method for saving the corners to a txt
        """
        with open(address + '\\box.txt', 'w+') as file:         # Open the text file
            box = ' '.join(['x'.join(map(str, x)) for x in self.box])     # Format the box string
            file.writelines(box)                                # Save the box string

    def read_box(self, address):
        """
        Method for reading the box document
        """
        with open(address + '\\box.txt') as file:                               # Open the text file
            self.box = [tuple(x.split('x')) for x in file.read().split(' ')]    # Read the box from the file

    def screenshot_save(self, address):
        """
        Method for saving the current screen in the bounding box
        """
        box = tuple(sum(map(list, self.box), []))                   # Format the box
        im = pyscreenshot.grab(box)                                 # Take a screenshot in the box
        im.save(address + '\\screen' + str(self.counter) + '.png')  # Save the screenshot
        self.counter += 1                                           # Increment the counter

    def screenshot_compare(self, address):
        """
        Method for comparing the screen to a previous screenshot
        """
        box = tuple(sum(map(list, self.box), []))                               # Format the box
        im = pyscreenshot.grab(box)                                             # Take a screenshot in the bounding box
        master = Image.open(address + '\\screen' + str(self.counter) + '.png')  # Grab the corresponding screenshot
        self.counter += 1                                                       # Increment the counter
        self.bool = (list(im.getdata()) == list(master.getdata()))              # Compare the screenshots


class Macro:
    """
    Macro class for handling the macro scripts and runs
    Attributes:
        mouse: a Mouse object for handling the mouse
        keyboard: a Keyboard object for handling the keyboard
        timer: a Timer object for timing the actions
        document: a Document class for saving and reading the actions to be performed
        address: The directory of the macro data
        directions: formatted actions that can be run with the eval function
        running: bool: True if controlling, False otherwise
        macro_time: length of each loop of the macro
    Methods:
        listen: when called it will listen to the keyboard and mouse and save it to the document until enter is pressed
        interpret_document: method for reformatting the strings in the document to directions with timestamps
        run: when called will loop the macro until enter is pressed
    """
    def __init__(self):
        self.mouse = Mouse()            # Initialize the mouse
        self.keyboard = Keyboard()      # Initialize the keyboard
        self.timer = Timer()            # Initialize the timer
        self.screen = Screen()          # Initialize the screen

        if 'y' in input('Would you like to use a previous macro?\n').lower():
            # If yes then waits for a valid address
            address = input('Browser name for the macro\n')
            while not os.path.exists(address):
                address = input('Invalid Browser. Please enter a valid Browser\n')
            self.address = address                      # Save the directory address
            self.screen.read_box(self.address)          # Read the saved bounding box

        else:
            # Otherwise wait for new filename
            address = input('Please provide the Browser that the new macro works in\n')
            self.address = address                      # Save the directory address
            self.document = Document(address, False)    # Initialize the document

            if not os.path.exists(address):
                os.makedirs(address)  # If the project folder does not exist, create it

            input('Press enter to start')               # Wait for user to continue
            self.screen.get_box()                       # Get the area of the screen to focus on
            self.screen.save_box(address)               # Save the area
            input('Press enter to start listening')     # Wait for user to continue
            self.listen()                               # Start the listener
            self.document.save()                        # Save the new macro
            self.screen.counter = 1                     # Reset the screenshot counter

        self.document = Document(address, True)         # Initialize the document with the saved macro
        self.directions = self.interpret_document()     # Interpret directions
        self.running = False                            # Initialize running
        self.macro_time = self.directions[-1][0]        # Set length of the macro by the last timestamp
        self.screenshots = sum([1 for x in self.directions if 'screenshot' in x[1]])

    def listen(self):
        """
        Saves all inputs from the user into the document until user presses enter
        """
        # Set behavior when user clicks so the click is saved with the time
        def m_on_click(x, y, button, pressed):
            if pressed:
                s = str(self.timer.check()) + ':\tclick(' + ', '.join(['pynput.mouse.' + str(button),
                                                                       str(x), str(y)]) + ')'
                self.document.append(s)

        # Same but with key presses
        def k_on_press(key):
            if key == pynput.keyboard.Key.enter:
                return False
            elif key == pynput.keyboard.Key.esc:
                self.screen.screenshot_save(self.address)
                s = str(self.timer.check()) + ':\tscreenshot'
                self.document.append(s)
            else:
                if 'Key' in str(key):
                    s = str(self.timer.check()) + ':\tkey_press(pynput.keyboard.' + str(key) + ')'
                else:
                    s = str(self.timer.check()) + ':\tkey_press(' + str(key) + ')'
                self.document.append(s)

        # Same but with key releases
        def k_on_release(key):
            if 'Key' in str(key):
                s = str(self.timer.check()) + ':\tkey_release(pynput.keyboard.' + str(key) + ')'
            else:
                s = str(self.timer.check()) + ':\tkey_release(' + str(key) + ')'
            self.document.append(s)

        m_listener = pynput.mouse.Listener(on_click=m_on_click)     # Initialize a pynput mouse listener
        k_listener = pynput.keyboard.Listener(on_press=k_on_press, on_release=k_on_release)  # Same for keyboard

        print('Press enter to stop listening')
        self.timer.start()  # Start timer
        m_listener.start()  # Start mouse listener
        k_listener.start()  # Start keyboard listener
        k_listener.join()   # Don't stop until enter is pressed (the listener returns False then)
        m_listener.stop()   # Stop the mouse listener when the keyboard listener stops

    def interpret_document(self) -> list:
        """
        Method for interpreting the document to be evaluated with the eval function
        Returns:
            list: tuples of timestamps with directions
        """
        out_list = []                                   # Initialize the output list
        for entry in self.document.document[:-1]:       # Loop through all the entries in the document
            entry = entry.split(':\t')                  # Split into timestamp and direction

            entry[0] = float(entry[0])                  # Typecast timestamp to float
            if 'click' in entry[1]:
                entry[1] = 'self.mouse.' + entry[1]     # If float then save with 'self.mouse.' for the eval function
            elif 'key' in entry[1]:
                entry[1] = 'self.keyboard.' + entry[1]  # Same but for keyboard actions
            else:
                entry[1] = 'self.screen.' + entry[1] + f'_compare(\'{self.address}\')'

            out_list.append((float(entry[0]), entry[1]))  # Append the order to output list
        return out_list     # Return the new set of directions

    def run(self):
        """
        Method for handling the running loop of the macro
        """
        # Behavior on keypress to allow for enter to interrupt the macro
        def on_press(key):
            if key == pynput.keyboard.Key.enter:
                self.running = False
                print('Stopped by the user')

        listener = pynput.keyboard.Listener(on_press=on_press)  # Initialize a listener to allow interruption
        listener.start()                                        # Start the listener

        print('Press enter to stop the macro')
        self.running = True                         # Set running to True to run the while loop
        self.timer.start()                          # Start the timer
        while self.running:
            order = self.directions[0]              # Find the next order
            if order[0] <= self.timer.check():      # If current time is past or at the timestamp then act
                eval(order[1])                      # Interpret the direction
                if not self.screen.bool:
                    self.running = False            # Stop if the screen is not what is expected
                    print('Unexpected difference found!')
                if self.screen.counter > self.screenshots:
                    self.screen.counter = 1         # Loop the screen counter
                self.directions.pop(0)              # Remove the direction to set new next move
                self.directions.append((float(order[0]) + self.macro_time, order[1]))  # Re-append the direction at end
        listener.stop()     # Stop the listener when the loop stops


Handler = Macro()
input('\nPress enter to start the macro')
Handler.run()
