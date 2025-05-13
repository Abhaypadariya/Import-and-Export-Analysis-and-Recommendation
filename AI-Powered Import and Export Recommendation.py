import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd

# Global variable to store full dataframe
global_df = None

def load_and_process_file():
    global global_df
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv")],
        title="Select your dataset"
    )

    if not file_path:
        return

    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip().str.lower()

        required_cols = ['item', 'area', 'import', 'export', 'production', 'consumption']
        if not all(col in df.columns for col in required_cols):
            messagebox.showerror("Error", "Dataset must contain: " + ", ".join(required_cols))
            return

        # Clean data
        df['import'] = df['import'].clip(lower=0)
        df['consumption'] = df['consumption'].clip(lower=0)

        df['demand'] = df['import'] + df['consumption']
        df['profit_margin'] = df['export'] - df['production']
        df['demand_score'] = df['demand'] / df['demand'].max()
        df['profit_score'] = df['profit_margin'] / df['profit_margin'].max()
        df['recommendation_score'] = 0.6 * df['demand_score'] + 0.4 * df['profit_score']

        # Store in global variable
        global_df = df.copy()

        # Populate item dropdown
        unique_items = sorted(df['item'].dropna().unique())
        item_dropdown['values'] = unique_items
        item_dropdown.set("Select Item")
        messagebox.showinfo("Success", "Dataset loaded successfully. Now choose an item.")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load file:\n{e}")

def show_top_countries():
    global global_df
    selected_item = item_dropdown.get()
    if not selected_item or selected_item == "Select Item":
        messagebox.showwarning("Warning", "Please select an item from the dropdown.")
        return

    if global_df is None:
        messagebox.showerror("Error", "Please load a dataset first.")
        return

    df_item = global_df[global_df['item'] == selected_item]
    if df_item.empty:
        messagebox.showinfo("Info", "No data found for selected item.")
        return

    # Get top 10 countries for selected item
    df_sorted = df_item.sort_values(by='recommendation_score', ascending=False)
    top_countries = df_sorted.drop_duplicates(subset='area').head(10)
    top_display = top_countries[['area', 'demand', 'profit_margin', 'recommendation_score']]

    # Clear old table data
    for row in tree.get_children():
        tree.delete(row)

    # Update table headers
    tree["columns"] = list(top_display.columns)
    for col in top_display.columns:
        tree.heading(col, text=col.title().replace('_', ' '))
        tree.column(col, width=200, anchor="center")

    # Insert new rows
    for _, row in top_display.iterrows():
        tree.insert("", tk.END, values=list(row))


# --- GUI Setup ---
root = tk.Tk()
root.title("AI-Powered Import and Export Analysis and Recommendation")
root.geometry("1100x600")

# Load CSV button
load_btn = ttk.Button(root, text="Load Dataset", command=load_and_process_file)
load_btn.pack(pady=10)

# Dropdown for item selection
item_dropdown = ttk.Combobox(root, state="readonly", width=60)
item_dropdown.pack(pady=5)

# Button to show top countries for selected item
show_btn = ttk.Button(root, text="Show Top 10 Countries", command=show_top_countries)
show_btn.pack(pady=5)

# Treeview for results
tree = ttk.Treeview(root, show="headings")
tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Start GUI
root.mainloop()
