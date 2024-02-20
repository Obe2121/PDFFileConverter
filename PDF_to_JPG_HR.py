import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import fitz  # PyMuPDF
import os
from PIL import Image, ImageTk

def create_thumbnail(pdf_path, thumbnail_size=(100, 100)):
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(0)
    pix = page.get_pixmap()
    pil_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    pdf_document.close()
    thumbnail = pil_image.resize(thumbnail_size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(thumbnail)

def update_treeview():
    treeview.delete(*treeview.get_children())  # Clear existing entries
    for i, pdf_path in enumerate(selected_files):
        thumbnail = create_thumbnail(pdf_path)
        treeview.insert("", 'end', iid=i, text=os.path.basename(pdf_path), image=thumbnail)
        treeview.image_dict[i] = thumbnail  # Store reference to the image

def convert_to_jpg(pdf_file):
    folder_name = os.path.basename(os.path.dirname(pdf_file))
    radio_button_name = get_radio_button_name()
    if radio_button_name:
        base_name = f"{folder_name}_{radio_button_name}.jpg"
    else:
        base_name = f"{os.path.splitext(os.path.basename(pdf_file))[0]}.jpg"

    pdf_document = fitz.open(pdf_file)
    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        image = page.get_pixmap()
        image.save(os.path.join(os.path.dirname(pdf_file), base_name))

    pdf_document.close()

def browse_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    for file_path in file_paths:
        if file_path not in selected_files:
            selected_files.append(file_path)
    update_treeview()

def remove_file():
    selected_item = treeview.selection()
    if selected_item:
        index = treeview.index(selected_item)
        selected_files.pop(index)
        update_treeview()  # Refresh the treeview

def run_conversion():
    selected_item = treeview.selection()
    if not selected_item:
        messagebox.showinfo("No Selection", "Please select a file to convert.")
        return

    file_index = treeview.index(selected_item[0])
    pdf_path = selected_files[file_index]

    try:
        convert_to_jpg(pdf_path)
        # Remove the converted file from the list and Treeview
        selected_files.pop(file_index)
        treeview.delete(selected_item[0])
        messagebox.showinfo("Success", f"File converted and removed from the list: {os.path.basename(pdf_path)}")
    except Exception as e:
        messagebox.showerror("Conversion Error", f"Failed to convert {pdf_path}.\nError: {e}")

def rotate_pdf():
    selected_item = treeview.selection()
    if not selected_item:
        messagebox.showinfo("No Selection", "Please select a file to rotate.")
        return

    file_index = treeview.index(selected_item[0])
    pdf_path = selected_files[file_index]

    # Create a new file path
    new_pdf_path = pdf_path.replace('.pdf', '_rotated.pdf')

    # Rotate the PDF and save as a new file
    pdf_document = fitz.open(pdf_path)
    for page in pdf_document:
        page.set_rotation(page.rotation + 90)
    pdf_document.save(new_pdf_path)  # Save as a new file
    pdf_document.close()

    # Update the selected files list and regenerate the thumbnail
    selected_files[file_index] = new_pdf_path
    new_thumbnail = create_thumbnail(new_pdf_path)

    # Update the treeview
    treeview.item(selected_item, image=new_thumbnail)
    treeview.image_dict[file_index] = new_thumbnail

    # messagebox.showinfo("Rotation Complete", f"Rotated the pages of {os.path.basename(pdf_path)} and saved as {os.path.basename(new_pdf_path)}.")

def get_radio_button_name():
    selected_value = radio_value.get()
    for text, value in radio_options:
        if selected_value == value:
            if text == "Other":
                # Prompt user for custom name
                return simpledialog.askstring("Input", "Enter custom name:")
            return text
    return None

# Create GUI window
root = tk.Tk()
root.title("PDF to JPG Converter")
root.geometry("800x400")

# Create style object and configure Treeview style
style = ttk.Style(root)
style.configure('Treeview', rowheight=120)

# Create a main frame
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=1)

# Create Frame for Radio Buttons
radio_frame = tk.Frame(main_frame)  
radio_frame.pack(side=tk.LEFT, fill=tk.Y, pady=10, padx=10)

# Radio Button Options
radio_value = tk.IntVar()
radio_options = [
    ("Employee_Photo", 1),
    ("Photo_ID", 2),
    ("Referral_Letter", 3),
    ("Proof_of_Bank_Account", 4),
    ("Drug_Free_Card", 5),
    ("OSHA_10", 6),
    ("OSHA_30", 7),
    ("First_Aid/CPR", 8),
    ("Other", 9)
    ]

# Create Radio Buttons
for text, value in radio_options:
    tk.Radiobutton(radio_frame, text=text, variable=radio_value, value=value).pack(anchor=tk.W)

# Create Frame for Treeview and Scrollbars
treeview_frame = tk.Frame(main_frame)
treeview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

# Treeview
treeview = ttk.Treeview(treeview_frame, columns=('Files',), show='tree headings')
treeview.heading('#0', text='File')
treeview.column('#0', width=200)
treeview.image_dict = {}  # Dictionary to store image references

# Create Vertical Scrollbar
v_scroll = ttk.Scrollbar(treeview_frame, orient='vertical', command=treeview.yview)
treeview.configure(yscrollcommand=v_scroll.set)
v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

# Create Horizontal Scrollbar
h_scroll = ttk.Scrollbar(treeview_frame, orient='horizontal', command=treeview.xview)
treeview.configure(xscrollcommand=h_scroll.set)
h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

# Pack the treeview last so it fills the rest of the frame
treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

# Create Frame for Buttons
buttons_frame = tk.Frame(main_frame)
buttons_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

# Add buttons to the buttons frame
browse_button = tk.Button(buttons_frame, text="Browse PDF Files", command=browse_files)
browse_button.pack(pady=10, padx=20)

remove_button = tk.Button(buttons_frame, text="Remove File", command=remove_file)
remove_button.pack(pady=10, padx=20)

run_button = tk.Button(buttons_frame, text="Run", command=run_conversion)
run_button.pack(pady=10, padx=20)

rotate_button = tk.Button(buttons_frame, text="Rotate", command=rotate_pdf)
rotate_button.pack(pady=10, padx=20)

0# List to store selected files
selected_files = []

# Start the GUI event loop
root.mainloop()
