import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import json
import os

class ClipboardManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("One-Click Clipboard Manager")
        self.root.geometry("600x700")
        self.root.configure(bg='#ffffff')

        # Custom colors
        self.colors = {
            'primary': '#2563eb',
            'danger': '#dc2626',
            'background': '#ffffff',
            'card': '#f8fafc',
            'text': '#1e293b',
            'border': '#e2e8f0'
        }

        # Data storage
        self.items = []
        self.data_file = "clipboard_data.json"

        # Load saved data
        self.load_data()

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        # Title
        title_frame = tk.Frame(self.root, bg=self.colors['background'])
        title_frame.pack(fill='x', pady=(30, 20))

        title_label = tk.Label(
            title_frame,
            text="Clipboard Manager",
            font=("Segoe UI", 24, "bold"),
            bg=self.colors['background'],
            fg=self.colors['text']
        )
        title_label.pack()

        subtitle = tk.Label(
            title_frame,
            text="Store and manage your clipboard items with multiple contexts",
            font=("Segoe UI", 12),
            bg=self.colors['background'],
            fg='#64748b'
        )
        subtitle.pack(pady=(5, 0))

        # Items frame with scrollbar
        items_frame = tk.Frame(self.root, bg=self.colors['background'])
        items_frame.pack(pady=(10, 0), padx=40, fill='both', expand=True)

        # Scrollable canvas
        canvas = tk.Canvas(items_frame, bg=self.colors['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=self.colors['background'])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        self._canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        def update_scrollable_frame_width(event):
            canvas.itemconfig(self._canvas_window, width=event.width)
        canvas.bind("<Configure>", update_scrollable_frame_width)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Bottom Buttons Frame
        bottom_buttons_frame = tk.Frame(self.root, bg=self.colors['background'])
        bottom_buttons_frame.pack(pady=(15, 25), fill='x')

        inner_buttons_container = tk.Frame(bottom_buttons_frame, bg=self.colors['background'])
        inner_buttons_container.pack()

        # Add with multiple contexts button
        add_btn = tk.Button(
            inner_buttons_container,
            text="Add Item",
            command=self.add_item_with_contexts,
            bg=self.colors['primary'],
            fg='white',
            font=("Segoe UI", 11, "bold"),
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2'
        )
        add_btn.pack(side='left', padx=(0, 10))
        self.create_hover_effect(add_btn, '#1d4ed8', self.colors['primary'])

        # Clear all button
        clear_btn = tk.Button(
            inner_buttons_container,
            text="Clear All Items",
            command=self.clear_all,
            bg='white',
            fg=self.colors['danger'],
            font=("Segoe UI", 10, "bold"),
            relief='solid',
            borderwidth=1,
            padx=20,
            pady=7,
            cursor='hand2'
        )
        clear_btn.pack(side='left', padx=(10, 0))
        self.create_hover_effect(clear_btn, '#fee2e2', 'white')

        # Load existing items
        self.refresh_items()

    def create_hover_effect(self, widget, color_on_hover, color_on_leave):
        widget.bind("<Enter>", lambda e: widget.configure(bg=color_on_hover))
        widget.bind("<Leave>", lambda e: widget.configure(bg=color_on_leave))

    def add_item_with_contexts(self):
        """Adds an item with multiple context fields."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Clipboard Item with Contexts")
        dialog.geometry("500x600")
        dialog.configure(bg=self.colors['background'])
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, 
                                   self.root.winfo_rooty() + 50))

        # Main container with scrollbar
        main_frame = tk.Frame(dialog, bg=self.colors['background'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Title input
        title_frame = tk.Frame(main_frame, bg=self.colors['background'])
        title_frame.pack(fill='x', pady=(0, 15))

        title_label = tk.Label(
            title_frame, 
            text="Title:", 
            font=("Segoe UI", 11, "bold"), 
            bg=self.colors['background'],
            fg=self.colors['text']
        )
        title_label.pack(anchor='w')

        title_entry = tk.Entry(
            title_frame,
            font=("Segoe UI", 10),
            width=50,
            border=1,
            relief='solid'
        )
        title_entry.pack(fill='x', pady=(5, 0))

        # Contexts frame with scrollbar
        contexts_label = tk.Label(
            main_frame, 
            text="Contexts:", 
            font=("Segoe UI", 11, "bold"), 
            bg=self.colors['background'],
            fg=self.colors['text']
        )
        contexts_label.pack(anchor='w', pady=(0, 5))

        # Scrollable frame for contexts
        contexts_canvas = tk.Canvas(main_frame, bg=self.colors['background'], highlightthickness=0, height=300)
        contexts_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=contexts_canvas.yview)
        contexts_scrollable_frame = tk.Frame(contexts_canvas, bg=self.colors['background'])

        contexts_scrollable_frame.bind(
            "<Configure>",
            lambda e: contexts_canvas.configure(scrollregion=contexts_canvas.bbox("all"))
        )

        contexts_canvas.create_window((0, 0), window=contexts_scrollable_frame, anchor="nw")
        contexts_canvas.configure(yscrollcommand=contexts_scrollbar.set)

        contexts_canvas.pack(side="left", fill="both", expand=True)
        contexts_scrollbar.pack(side="right", fill="y")

        # Store context entries
        context_entries = []

        def add_context_field():
            context_frame = tk.Frame(contexts_scrollable_frame, bg=self.colors['card'], 
                                   relief='solid', borderwidth=1, padx=10, pady=8)
            context_frame.pack(fill='x', pady=5, padx=2)

            # Context label
            label_frame = tk.Frame(context_frame, bg=self.colors['card'])
            label_frame.pack(fill='x', pady=(0, 5))

            tk.Label(label_frame, text="Label:", font=("Segoe UI", 9), 
                    bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
            
            label_entry = tk.Entry(label_frame, font=("Segoe UI", 9), width=20, 
                                 border=1, relief='solid')
            label_entry.pack(fill='x')

            # Context value
            value_frame = tk.Frame(context_frame, bg=self.colors['card'])
            value_frame.pack(fill='x', pady=(5, 0))

            tk.Label(value_frame, text="Value:", font=("Segoe UI", 9), 
                    bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
            
            value_entry = tk.Entry(value_frame, font=("Segoe UI", 9), width=30, 
                                 border=1, relief='solid')
            value_entry.pack(fill='x')

            # Remove button
            remove_btn = tk.Button(
                context_frame,
                text="Remove",
                command=lambda: remove_context_field(context_frame),
                bg=self.colors['danger'],
                fg='white',
                font=("Segoe UI", 8),
                relief='flat',
                padx=8,
                pady=3,
                cursor='hand2'
            )
            remove_btn.pack(anchor='e', pady=(5, 0))

            context_entries.append((label_entry, value_entry, context_frame))
            contexts_scrollable_frame.update_idletasks()

        def remove_context_field(frame):
            # Find and remove the context entry
            for i, (label_entry, value_entry, context_frame) in enumerate(context_entries):
                if context_frame == frame:
                    context_entries.pop(i)
                    break
            frame.destroy()
            contexts_scrollable_frame.update_idletasks()

        # Add initial context fields
        add_context_field()
        add_context_field()
        add_context_field()

        # Add context button
        add_context_btn = tk.Button(
            main_frame,
            text="+ Add Context",
            command=add_context_field,
            bg='#10b981',
            fg='white',
            font=("Segoe UI", 9, "bold"),
            relief='flat',
            padx=15,
            pady=5,
            cursor='hand2'
        )
        add_context_btn.pack(pady=(10, 15))
        self.create_hover_effect(add_context_btn, '#059669', '#10b981')

        # Button frame
        btn_frame = tk.Frame(main_frame, bg=self.colors['background'])
        btn_frame.pack(fill='x', pady=(10, 0))

        def save_item():
            title = title_entry.get().strip()
            
            if not title:
                messagebox.showwarning("Warning", "Please enter a title.")
                return

            # Collect contexts
            contexts = []
            for label_entry, value_entry, _ in context_entries:
                label = label_entry.get().strip()
                value = value_entry.get().strip()
                if label and value:  # Only add if both label and value are provided
                    contexts.append({"label": label, "value": value})

            if not contexts:
                messagebox.showwarning("Warning", "Please add at least one context with both label and value.")
                return

            # Check if title already exists
            for item in self.items:
                if isinstance(item, dict) and item.get('title') == title:
                    messagebox.showinfo("Info", "An item with this title already exists!")
                    return

            # Add new item with contexts
            new_item = {
                'title': title, 
                'contexts': contexts,
                'type': 'multi_context'
            }
            self.items.append(new_item)
            self.refresh_items()
            self.save_data()
            dialog.destroy()

        save_btn = tk.Button(
            btn_frame,
            text="Save",
            command=save_item,
            bg=self.colors['primary'],
            fg='white',
            font=("Segoe UI", 10, "bold"),
            relief='flat',
            padx=15,
            pady=5,
            cursor='hand2'
        )
        save_btn.pack(side='right')
        self.create_hover_effect(save_btn, '#1d4ed8', self.colors['primary'])

        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            bg='white',
            fg=self.colors['text'],
            font=("Segoe UI", 10),
            relief='solid',
            borderwidth=1,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        cancel_btn.pack(side='right', padx=(0, 10))
        self.create_hover_effect(cancel_btn, '#f1f5f9', 'white')

    def copy_to_clipboard(self, text):
        if text:
            pyperclip.copy(text)
            messagebox.showinfo("Success", "Text copied to clipboard!")
        else:
            messagebox.showinfo("Error", "Nothing to copy.")

    def delete_item(self, item):
        if item in self.items:
            self.items.remove(item)
            self.refresh_items()
            self.save_data()

    def refresh_items(self):
        # Clear existing items
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Create item frames for each item in reverse order (newest on top)
        for item in reversed(self.items):
            # Handle both old format (string/dict with content) and new format (dict with contexts)
            if isinstance(item, dict) and item.get('type') == 'multi_context':
                self.create_multi_context_item(item)
            elif isinstance(item, dict):
                # Old format with title and content
                self.create_simple_item(item)
            else:
                # Very old format (just string)
                self.create_simple_item({'title': 'Untitled', 'content': str(item)})

    def create_multi_context_item(self, item):
        """Create a display for multi-context items."""
        item_title = item.get('title', 'Untitled')
        contexts = item.get('contexts', [])

        # Main item frame
        item_frame = tk.Frame(
            self.scrollable_frame,
            bg=self.colors['card'],
            padx=15,
            pady=15,
            borderwidth=1,
            relief="solid",
            highlightbackground=self.colors['border']
        )
        item_frame.pack(fill='x', pady=8, padx=5, ipady=5, ipadx=5)

        # Title label
        title_label = tk.Label(
            item_frame,
            text=item_title,
            justify='left',
            anchor='w',
            bg=self.colors['card'],
            fg=self.colors['primary'],
            font=("Segoe UI", 12, "bold"),
            padx=5
        )
        title_label.pack(fill='x', anchor='w', pady=(0, 10))

        # Contexts frame
        contexts_frame = tk.Frame(item_frame, bg=self.colors['card'])
        contexts_frame.pack(fill='x', pady=(0, 10))

        for i, context in enumerate(contexts):
            context_row = tk.Frame(contexts_frame, bg=self.colors['card'])
            context_row.pack(fill='x', pady=2)

            # Context label
            label_text = tk.Label(
                context_row,
                text=f"{context['label']}:",
                font=("Segoe UI", 9, "bold"),
                bg=self.colors['card'],
                fg=self.colors['text'],
                width=12,
                anchor='w'
            )
            label_text.pack(side='left', padx=(5, 10))

            # Context value
            value_text = tk.Label(
                context_row,
                text=context['value'],
                font=("Segoe UI", 9),
                bg=self.colors['card'],
                fg=self.colors['text'],
                anchor='w'
            )
            value_text.pack(side='left', fill='x', expand=True)

            # Copy button for individual context
            copy_context_btn = tk.Button(
                context_row,
                text="Copy",
                command=lambda v=context['value']: self.copy_to_clipboard(v),
                bg='#10b981',
                fg='white',
                font=("Segoe UI", 8),
                relief='flat',
                padx=8,
                pady=2,
                cursor='hand2'
            )
            copy_context_btn.pack(side='right', padx=(5, 0))
            self.create_hover_effect(copy_context_btn, '#059669', '#10b981')

        # Button frame
        btn_frame = tk.Frame(item_frame, bg=self.colors['card'])
        btn_frame.pack(fill='x', pady=(10, 0))

        # Copy all button
        all_text = "\n".join([f"{ctx['label']}: {ctx['value']}" for ctx in contexts])
        copy_all_btn = tk.Button(
            btn_frame,
            text="Copy All",
            command=lambda: self.copy_to_clipboard(all_text),
            bg=self.colors['primary'],
            fg='white',
            font=("Segoe UI", 9, "bold"),
            relief='flat',
            padx=12,
            pady=5,
            cursor='hand2'
        )
        copy_all_btn.pack(side='left')
        self.create_hover_effect(copy_all_btn, '#1d4ed8', self.colors['primary'])

        # Delete button
        del_btn = tk.Button(
            btn_frame,
            text="Delete",
            command=lambda i=item: self.delete_item(i),
            bg=self.colors['danger'],
            fg='white',
            font=("Segoe UI", 9, "bold"),
            relief='flat',
            padx=12,
            pady=5,
            cursor='hand2'
        )
        del_btn.pack(side='right')
        self.create_hover_effect(del_btn, '#b91c1c', self.colors['danger'])

    def create_simple_item(self, item):
        """Create a display for simple items (backward compatibility)."""
        item_title = item.get('title', 'Untitled')
        item_content = item.get('content', '')

        item_frame = tk.Frame(
            self.scrollable_frame,
            bg=self.colors['card'],
            padx=10,
            pady=10,
            borderwidth=1,
            relief="solid",
            highlightbackground=self.colors['border']
        )
        item_frame.pack(fill='x', pady=8, padx=5, ipady=5, ipadx=5)

        # Title label
        title_label = tk.Label(
            item_frame,
            text=item_title,
            justify='left',
            anchor='w',
            bg=self.colors['card'],
            fg=self.colors['primary'],
            font=("Segoe UI", 11, "bold"),
            padx=5
        )
        title_label.pack(fill='x', anchor='w')

        # Content frame
        content_frame = tk.Frame(item_frame, bg=self.colors['card'], padx=0, pady=5)
        content_frame.pack(fill='x', expand=True)

        # Content label
        item_label = tk.Label(
            content_frame,
            text=item_content,
            justify='left',
            anchor='w',
            bg=self.colors['card'],
            fg=self.colors['text'],
            font=("Segoe UI", 10),
            padx=5,
            pady=5,
            wraplength=480
        )
        item_label.pack(fill='both', expand=True, anchor='w')

        # Button frame
        btn_frame = tk.Frame(item_frame, bg=self.colors['card'], padx=5, pady=0)
        btn_frame.pack(fill='x', side='bottom')

        # Copy button
        copy_btn = tk.Button(
            btn_frame,
            text="Copy",
            command=lambda t=item_content: self.copy_to_clipboard(t),
            bg=self.colors['primary'],
            fg='white',
            font=("Segoe UI", 9, "bold"),
            relief='flat',
            padx=10,
            pady=5,
            cursor='hand2'
        )
        copy_btn.pack(side='left', padx=(0, 8))
        self.create_hover_effect(copy_btn, '#1d4ed8', self.colors['primary'])

        # Delete button
        del_btn = tk.Button(
            btn_frame,
            text="×",
            command=lambda i=item: self.delete_item(i),
            bg=item_frame['bg'],
            fg=self.colors['danger'],
            font=("Segoe UI", 16, "bold"),
            relief='flat',
            width=2,
            cursor='hand2',
            borderwidth=0
        )
        del_btn.pack(side='right')
        self.create_hover_effect(del_btn, '#fee2e2', self.colors['card'])

    def clear_all(self):
        if self.items and messagebox.askyesno("Confirm", "Are you sure you want to clear all clipboard items?"):
            self.items.clear()
            self.refresh_items()
            self.save_data()
        elif not self.items:
            messagebox.showinfo("Info", "There are no items to clear.")

    def save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.items, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")
            messagebox.showerror("Error", f"Could not save data: {e}")

    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    loaded_items = json.load(f)
                    if isinstance(loaded_items, list):
                        self.items = loaded_items
                    else:
                        self.items = []
            else:
                self.items = []
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {self.data_file}. Starting with an empty list.")
            self.items = []
        except Exception as e:
            print(f"Error loading data: {e}")
            messagebox.showerror("Error", f"Could not load data: {e}")
            self.items = []

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        self.save_data()
        self.root.destroy()

if __name__ == "__main__":
    app = ClipboardManager()
    app.run()