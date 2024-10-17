import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from file_loader import FileLoader
from text_processor import TextProcessor

import threading

class UIComponent:
    def __init__(self, parent, text_processor, new_algorithm_processor):
        self.parent = parent
        self.text_processor = text_processor
        self.new_algorithm_processor = new_algorithm_processor
        self.create_widgets()

    def create_widgets(self):
        self.create_header()
        self.create_columns()
        # Configure main window grid
        self.parent.grid_rowconfigure(0, weight=0)  # Header row
        self.parent.grid_rowconfigure(1, weight=1)  # Columns row
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)
        self.parent.grid_columnconfigure(2, weight=1)

    def show_memo_table(self):
        memo_modal = tk.Toplevel(self.parent)
        memo_modal.title("Memo Table")
        memo_modal.geometry("600x400")
        memo_modal.config(bg='#232323')  # Set background to dark
        tk.Label(memo_modal, text="Memo Table content goes here", bg='#232323', fg='#E0E0E0').pack(pady=20)
        tk.Button(memo_modal, text="Close", command=memo_modal.destroy, bg='#ABDBE6', fg='white').pack(pady=10)

    def create_header(self):
        header_frame = tk.Frame(self.parent, background='#121212')
        header_frame.grid(row=0, column=0, columnspan=3, sticky='ew')

        screen_width = self.parent.winfo_screenwidth()

        tk.Label(header_frame, text="Adaptive Dynamic Approach Applied in Text Summarization",
                 font=('Slussen Mono', 15), fg="white", bg="#121212", wraplength=screen_width * 0.45).pack(pady=15)

        self.summarizer = tk.Button(header_frame, text='Summarize', borderwidth=1, state='disabled', 
                                     width=12, height=2, activebackground='#FF5555', 
                                     activeforeground="gray", disabledforeground='#555555', font=('Lato Bold', 9), 
                                     cursor='X_cursor', command=self.on_summarize_click, bg='#232323', fg='white')
        self.summarizer.pack(side=tk.RIGHT, padx=5)

        tk.Button(header_frame, text='Presentation of Data', borderwidth=1, 
                width=16, height=2, activebackground='#ABDBE6', activeforeground="white",
                disabledforeground='#555555', font=('Lato Bold', 9), cursor='X_cursor',
                bg='#232323', fg='white', command=self.open_presentation_modal).pack(side=tk.RIGHT, padx=5)

        tk.Button(header_frame, text='About', borderwidth=1, state='normal', 
                  width=12, height=2, activebackground='#ABDBE6', activeforeground="white",
                  font=('Lato Bold', 9), cursor='hand2', bg='#232323', fg='white', command=self.open_about_modal).pack(side=tk.RIGHT, padx=5)

        self.memo_button = tk.Button(header_frame, text='Show Memo Table', borderwidth=1, state='disabled',
                                     width=15, height=2, activebackground='#ABDBE6', 
                                     activeforeground="white", disabledforeground='#555555', font=('Lato Bold', 9), 
                                     cursor='hand2', bg='#232323', fg='white', command=self.show_memo_table)
        self.memo_button.pack(side=tk.RIGHT, padx=5)

        self.clear_button = tk.Button(header_frame, text='Clear All', borderwidth=1, state='normal', 
                                      width=12, height=2, activebackground='#ABDBE6', 
                                      activeforeground="white", font=('Lato Bold', 9), cursor='hand2', bg='#232323', fg='white', 
                                      command=self.clear_all_data)
        self.clear_button.pack(side=tk.RIGHT, padx=5)

    def create_columns(self):
        self.create_column1()
        self.create_column2()
        self.create_column3()

    def create_column1(self):
        self.column1 = tk.Frame(self.parent, width=300, height=500, padx=15, pady=2, borderwidth=1, relief='groove', background='#232323')
        self.column1.grid(row=1, column=0)
        self.column1.grid_propagate(False)  # Prevents resizing

        tk.Label(self.column1, text='File Content Preview', pady=6, font=('Lato Bold', 15), background='#232323', fg='#E0E0E0').pack(side='top')

        self.file_content_text = tk.Text(self.column1, wrap='word', background='#121212', fg='#E0E0E0', insertbackground='white')
        self.file_content_text.pack(expand=True, fill=tk.BOTH)

        # Insert File button and File Destination label placed below the file content text
        button_frame = tk.Frame(self.column1, background='#232323')
        button_frame.pack(side='bottom', fill=tk.X, pady=5)

        self.insert_file_button = tk.Button(button_frame, text="Insert File", width=15, height=2, borderwidth=1, relief='ridge', cursor='hand2', bg='#C6DEF1', fg='white', command=self.on_open_file_click)
        self.insert_file_button.pack(side='left', padx=5)

        self.file_label = tk.Label(button_frame, text="File Destination", padx=5, background='#232323', fg='#E0E0E0')
        self.file_label.pack(side='right', padx=5)

    def create_column2(self):
        self.column2 = tk.Frame(self.parent, width=300, height=400, padx=15, pady=26, borderwidth=1, relief='groove', background='#232323')
        self.column2.grid(row=1, column=1)
        self.column2.grid_propagate(False)  # Prevents resizing

        tk.Label(self.column2, text='Existing Algorithm', pady=6, font=('Lato Bold', 15), background='#232323', fg='#E0E0E0').pack(side='top')

        self.resultsText = tk.Text(self.column2, wrap='word', state='disabled', background='#121212', fg='#E0E0E0', insertbackground='white')
        self.resultsText.pack(expand=True, fill=tk.BOTH)

    def create_column3(self):
        self.column3 = tk.Frame(self.parent, width=300, height=400, padx=15, pady=26, borderwidth=1, relief='groove', background='#232323')
        self.column3.grid(row=1, column=2)
        self.column3.grid_propagate(False)  # Prevents resizing

        tk.Label(self.column3, text='New Algorithm', pady=6, font=('Lato Bold', 15), background='#232323', fg='#E0E0E0').pack(side='top')

        self.newAlgoResultsText = tk.Text(self.column3, wrap='word', state='disabled', background='#121212', fg='#E0E0E0', insertbackground='white')
        self.newAlgoResultsText.pack(expand=True, fill=tk.BOTH)

    def on_open_file_click(self):
        file_loader = FileLoader()
        filename, file_content = file_loader.open_file()

        if not filename or not file_content:
            messagebox.showerror("Error", "No file selected or file content is empty.")
            return

        self.file_label.config(text=filename)
        self.file_content_text.delete(1.0, tk.END)
        self.file_content_text.insert(tk.END, file_content)

        self.text_processor.set_content(file_content)
        self.summarizer.config(state='normal')
        self.memo_button.config(state='normal')

    def on_summarize_click(self):
        # Check if there is content in text_processor
        if not self.text_processor.get_content():
            messagebox.showerror("Error", "No content found in text_processor.")
            return

        # Generate summary using the existing algorithm
        summary = self.text_processor.generate_summary()  # Use the correct method name

        # Configure the title tag for existing algorithm
        self.resultsText.tag_config("title", foreground="green", font=("Helvetica", 12, "bold"))
        self.resultsText.config(state='normal')
        self.resultsText.delete(1.0, tk.END)
        self.resultsText.insert(tk.END, f"{self.text_processor.title}\n\n", "title")  # Insert title with tag
        self.resultsText.insert(tk.END, summary)  # Insert summary without tag
        self.resultsText.config(state='disabled')

        # Prepare for new algorithm summarization
        self.new_algorithm_processor.set_content(self.text_processor.get_content())

        # Generate new algorithm summary
        new_algo_summary = self.new_algorithm_processor.generate_summary()

        # Check if new_algo_summary has a valid value
        if new_algo_summary is None or new_algo_summary == "":
            messagebox.showerror("Error", "Failed to generate summary using the new algorithm.")
            return

        # Get the title from the NewAlgorithmProcessor
        new_algo_title = self.new_algorithm_processor.get_title()

        # Display the new algorithm summary with the title
        self.newAlgoResultsText.tag_config("title", foreground="green", font=("Helvetica", 12, "bold"))
        self.newAlgoResultsText.config(state='normal')
        self.newAlgoResultsText.delete(1.0, tk.END)
        self.newAlgoResultsText.insert(tk.END, f"{new_algo_title}\n\n", "title")  # Insert file title with tag
        self.newAlgoResultsText.insert(tk.END, new_algo_summary)  # Insert new algorithm summary without tag
        self.newAlgoResultsText.config(state='disabled')




    def clear_all_data(self):
        self.file_label.config(text="File Destination")
        self.file_content_text.delete(1.0, tk.END)
        self.resultsText.config(state='normal')
        self.resultsText.delete(1.0, tk.END)
        self.resultsText.config(state='disabled')
        self.newAlgoResultsText.config(state='normal')
        self.newAlgoResultsText.delete(1.0, tk.END)
        self.newAlgoResultsText.config(state='disabled')
        self.summarizer.config(state='disabled')
        self.memo_button.config(state='disabled')

    def open_about_modal(self):
        about_modal = tk.Toplevel(self.parent)
        about_modal.title("About")
        about_modal.geometry("300x200")
        tk.Label(about_modal, text="This is a text summarization application.", padx=10, pady=10).pack()
        tk.Button(about_modal, text="Close", command=about_modal.destroy).pack(pady=20)



    def open_presentation_modal(self):
        # Ensure that summaries are generated before presenting data
        if not self.text_processor.generated_summary or not self.new_algorithm_processor.generated_summary:
            tk.messagebox.showerror("Error", "Please generate summaries before viewing evaluation scores.")
            return

        # Set original text for evaluation
        original_text = self.text_processor.get_reference_summary()
        self.new_algorithm_processor.set_original_text(original_text)

        # Calculate word count for the original text
        original_word_count = len(original_text.split())

        # New window for presentation
        presentation_modal = tk.Toplevel(self.parent)
        presentation_modal.title("Presentation of Data")
        presentation_modal.geometry("600x400")
        presentation_modal.config(bg='#232323')

        # Treeview for displaying evaluation scores
        columns = ("Metric", "Existing Algorithm", "New Algorithm")
        metrics_tree = ttk.Treeview(presentation_modal, columns=columns, show='headings')
        metrics_tree.heading("Metric", text="Metric")
        metrics_tree.heading("Existing Algorithm", text="Existing Algorithm")
        metrics_tree.heading("New Algorithm", text="New Algorithm")

        # Scrollbar for Treeview
        scrollbar = ttk.Scrollbar(presentation_modal, orient=tk.VERTICAL, command=metrics_tree.yview)
        metrics_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a loading modal
        loading_modal = tk.Toplevel(self.parent)
        loading_modal.title("Loading")
        loading_modal.geometry("300x100")
        loading_modal.config(bg='#232323')

        loading_label = tk.Label(loading_modal, text="Loading...", bg='#232323', fg='white')
        loading_label.pack(pady=10)

        # Progress bar
        progress_bar = ttk.Progressbar(loading_modal, orient=tk.HORIZONTAL, length=250, mode='indeterminate')
        progress_bar.pack(pady=10)
        progress_bar.start()  # Start the progress bar animation

        # Start the loading animation and data calculation in a separate thread
        threading.Thread(target=self.show_presentation_data, args=(loading_modal, metrics_tree, original_text, original_word_count, progress_bar), daemon=True).start()

        # Configure the Treeview
        metrics_tree.pack(expand=True, fill=tk.BOTH)
        presentation_modal.mainloop()

    def show_presentation_data(self, loading_modal, metrics_tree, original_text, original_word_count, progress_bar):
        # Perform calculations for ROUGE and BERT scores
        existing_rouge = self.text_processor.get_rouge_scores()
        new_algorithm_rouge = self.new_algorithm_processor.get_rouge_scores()

        existing_summary = self.text_processor.generated_summary
        new_summary = self.new_algorithm_processor.generated_summary

        existing_bertscore = self.text_processor.calculate_bertscore(existing_summary, original_text)
        new_bertscore = self.new_algorithm_processor.calculate_bertscore(new_summary, original_text)

        existing_word_count = len(existing_summary.split())
        new_word_count = len(new_summary.split())

        # Insert metrics into the Treeview
        self.insert_metrics(metrics_tree, existing_rouge, new_algorithm_rouge, existing_bertscore, new_bertscore, original_word_count, existing_word_count, new_word_count)

        # Close the loading modal after a brief delay
        loading_modal.after(100, loading_modal.destroy)

        # Stop the progress bar
        progress_bar.stop()  # Stop the progress bar animation

    def insert_metrics(self, metrics_tree, existing_rouge, new_algorithm_rouge, existing_bertscore, new_bertscore, original_word_count, existing_word_count, new_word_count):
        # Insert ROUGE scores
        existing_rouge_l = existing_rouge[0]['rouge-l']
        new_rouge_l = new_algorithm_rouge[0]['rouge-l']

        # Insert ROUGE metrics
        metrics_tree.insert("", "end", values=("Rouge L", "", ""), tags=('colored_row',))
        metrics_tree.insert("", "end", values=("ROUGE-L Precision", existing_rouge_l['p'], new_rouge_l['p']))
        metrics_tree.insert("", "end", values=("ROUGE-L Recall", existing_rouge_l['r'], new_rouge_l['r']))
        metrics_tree.insert("", "end", values=("ROUGE-L F1-Score", existing_rouge_l['f'], new_rouge_l['f']))

        # Insert BERTScore metrics with limited decimals
        metrics_tree.insert("", "end", values=("BERTScore", "", ""), tags=('colored_row',))
        metrics_tree.insert("", "end", values=("BERT Precision", f"{existing_bertscore['precision']:.2f}", f"{new_bertscore['precision']:.2f}"))
        metrics_tree.insert("", "end", values=("BERT Recall", f"{existing_bertscore['recall']:.2f}", f"{new_bertscore['recall']:.2f}"))
        metrics_tree.insert("", "end", values=("BERT F1-Score", f"{existing_bertscore['f1']:.2f}", f"{new_bertscore['f1']:.2f}"))

        # Reference-Free Score
        existing_reference_free_score = self.text_processor.compute_reference_free_score()
        reference_free_score = self.new_algorithm_processor.compute_reference_free_score()

        # Insert Reference-Free Score
        metrics_tree.insert("", "end", values=("Reference-Free Score", f"{existing_reference_free_score:.2f}", f"{reference_free_score:.2f}"))

        # Insert Word Count for original and summarized content
        metrics_tree.insert("", "end", values=(" ", "", ""))
        metrics_tree.insert("", "end", values=("Original Content Word Count", original_word_count, original_word_count))
        metrics_tree.insert("", "end", values=("Summarized Content Word Count", existing_word_count, new_word_count))

        # Configure the tag for the colored row
        metrics_tree.tag_configure('colored_row', background='#C9E4DE')  # Change to your desired color
