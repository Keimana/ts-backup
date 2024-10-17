import tkinter as tk
from text_processor import TextProcessor
from newAlgorithmProcessor import NewAlgorithmProcessor
from userInterface import UIComponent  # Adjust the import according to your project structure

class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Text Summarization Application")
        self.root.geometry("900x600")  # Adjust size as needed

        # Initialize your text processor and new algorithm processor
        text_processor = TextProcessor()
        new_algorithm_processor = NewAlgorithmProcessor()

        # Create the UIComponent with the necessary processors
        self.ui = UIComponent(self.root, text_processor, new_algorithm_processor)
        
        # No need for pack() since UIComponent uses grid system for layout

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MainApp()
    app.run()
