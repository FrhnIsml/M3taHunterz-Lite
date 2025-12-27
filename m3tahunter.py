import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, ttk, simpledialog
from PIL import Image, ExifTags, ImageTk
import piexif
import os
import shutil
import tkintermapview
import styles

class MetaHunterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("M3taHunterz - OSINT Tool")
        self.root.geometry(styles.WINDOW_SIZE)
        self.root.configure(bg=styles.COLORS["bg_main"])

        self.current_image_path = None
        self.history_stack = []
        self.redo_stack = []
        self.logo_image_tk = None
        self.preview_image_tk = None 
        self.custom_tags_list = {}
        self.current_exif_dict = {} 

        # --- HEADER ---
        header_frame = tk.Frame(root, bg=styles.COLORS["bg_main"])
        header_frame.pack(pady=15)
        
        tk.Label(header_frame, text=styles.APP_TITLE_TEXT, font=styles.FONTS["header"], 
                 bg=styles.COLORS["bg_main"], fg=styles.COLORS["text_main"]).pack(side=tk.LEFT)

        # --- BUTTONS ---
        btn_frame = tk.Frame(root, bg=styles.COLORS["bg_main"])
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="📂 Load", command=self.browse_file, bg=styles.COLORS["btn_dark"], **styles.BTN_MAIN).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📋 Copy", command=self.copy_to_clipboard, bg=styles.COLORS["btn_dark"], **styles.BTN_MAIN).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="✏️ Fake", command=self.open_edit_window, bg=styles.COLORS["btn_warn"], fg="black", font=styles.FONTS["ui_bold"], width=12, height=2).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑️ Scrub", command=self.scrub_metadata, bg=styles.COLORS["btn_danger"], **styles.BTN_MAIN).pack(side=tk.LEFT, padx=5)
        
        tk.Frame(btn_frame, width=30, bg=styles.COLORS["bg_main"]).pack(side=tk.LEFT)
        
        # --- FIX: Removed Emojis, Added Clean Text ---
        self.btn_undo = tk.Button(btn_frame, text="<< Undo", command=self.undo_last_action, bg=styles.COLORS["btn_info"], state=tk.DISABLED, **styles.BTN_NAV)
        self.btn_undo.pack(side=tk.LEFT, padx=2)
        
        self.btn_redo = tk.Button(btn_frame, text="Redo >>", command=self.redo_last_action, bg=styles.COLORS["btn_info"], state=tk.DISABLED, **styles.BTN_NAV)
        self.btn_redo.pack(side=tk.LEFT, padx=2)

        # --- TABS ---
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background=styles.COLORS["bg_main"], borderwidth=0)
        style.configure('TNotebook.Tab', background="#333", foreground="white", padding=[10, 5])
        style.map('TNotebook.Tab', background=[('selected', styles.COLORS["text_main"])], foreground=[('selected', 'black')])

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True, fill="both")

        # --- TAB 1: METADATA ---
        self.tab_data = tk.Frame(self.notebook, bg=styles.COLORS["bg_main"])
        self.notebook.add(self.tab_data, text="   📄 Metadata   ")
        
        self.canvas = tk.Canvas(self.tab_data, bg=styles.COLORS["bg_panel"], highlightthickness=0)
        
        # SCROLLBAR: Uses 'sync_scroll' to move logo when dragging bar
        self.scrollbar = tk.Scrollbar(self.tab_data, orient="vertical", command=self.sync_scroll)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.text_id = None
        self.bg_logo_id = None
        self.full_text_content = "" 
        self.load_watermark()

        # --- TAB 2: MAP ---
        self.tab_map = tk.Frame(self.notebook, bg=styles.COLORS["bg_main"])
        self.notebook.add(self.tab_map, text="   🗺️ Live Map   ")

        self.map_left_frame = tk.Frame(self.tab_map, bg=styles.COLORS["bg_main"], width=300)
        self.map_left_frame.pack(side="left", fill="y", padx=10, pady=10)
        self.map_left_frame.pack_propagate(False)

        tk.Label(self.map_left_frame, text="Image Preview", font=styles.FONTS["ui_bold"], bg=styles.COLORS["bg_main"], fg=styles.COLORS["text_main"]).pack(pady=(0, 10))
        self.image_preview_label = tk.Label(self.map_left_frame, text="No Image Loaded", bg=styles.COLORS["bg_panel"], fg=styles.COLORS["text_dim"])
        self.image_preview_label.pack(fill="both", expand=True)

        self.map_right_frame = tk.Frame(self.tab_map, bg=styles.COLORS["bg_main"])
        self.map_right_frame.pack(side="right", fill="both", expand=True)

        self.map_widget = tkintermapview.TkinterMapView(self.map_right_frame, corner_radius=0, database_path="offline_map_cache.db")
        self.map_widget.pack(fill="both", expand=True)
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.map_widget.set_position(4.2105, 101.9758)
        self.map_widget.set_zoom(6)

        # --- BOTTOM BAR ---
        bottom_frame = tk.Frame(root, bg=styles.COLORS["bg_panel"], height=40)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Button(bottom_frame, text="🧹 Clear Map History", command=self.clear_map_cache, **styles.BTN_DANGER_SMALL).pack(side=tk.RIGHT, padx=20, pady=5)
        tk.Label(bottom_frame, text="Ready. Double-click any line to edit (Safe Mode).", bg=styles.COLORS["bg_panel"], fg="#888", font=styles.FONTS["small"]).pack(side=tk.LEFT, padx=20)

        # --- BINDINGS (SCROLL FIX) ---
        self.canvas.bind("<Configure>", self.center_watermark)
        
        # Mousewheel Bindings (Windows & Linux) to sync logo
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel) # Linux Up
        self.canvas.bind("<Button-5>", self.on_mousewheel) # Linux Down
        
        self.root.bind('<Control-z>', lambda e: self.undo_last_action())
        self.root.bind('<Control-y>', lambda e: self.redo_last_action())

    # ==================== LOGO & SCROLL LOGIC (NEW) ====================
    def load_watermark(self):
        if os.path.exists("logo.jpg"):
            try:
                img = Image.open("logo.jpg").convert("RGBA")
                img = img.resize((540, 450), Image.LANCZOS)
                alpha = img.split()[3]
                alpha = alpha.point(lambda p: p * 0.35)
                img.putalpha(alpha)
                self.watermark_img = ImageTk.PhotoImage(img)
                self.bg_logo_id = self.canvas.create_image(400, 300, image=self.watermark_img, anchor="center")
            except: pass

    def center_watermark(self, event=None):
        if not self.bg_logo_id: return
        
        # 1. Get Top-Left of CURRENT Visible Screen (Scroll Offset)
        x_start = self.canvas.canvasx(0)
        y_start = self.canvas.canvasy(0)
        
        # 2. Get Size of Visible Screen
        if event:
            w, h = event.width, event.height
        else:
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            
        # 3. Move Logo to Center of Visible Screen
        self.canvas.coords(self.bg_logo_id, x_start + w/2, y_start + h/2)
        self.canvas.tag_lower(self.bg_logo_id) # Keep behind text

    def sync_scroll(self, *args):
        # Called when Scrollbar is dragged
        self.canvas.yview(*args)
        self.center_watermark()

    def on_mousewheel(self, event):
        # Called when MouseWheel is used
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        self.center_watermark()

    # ==================== CORE FUNCTIONS ====================
    def browse_file(self):
        f = filedialog.askopenfilename(filetypes=[("JPEG", "*.jpg;*.jpeg")])
        if f: self.register_action(f)

    def register_action(self, p):
        if self.current_image_path: self.history_stack.append(self.current_image_path)
        self.redo_stack = []
        self.load_visuals(p)
        self.update_buttons()

    def load_visuals(self, p): 
        self.current_image_path = p
        self.display_metadata(p)
        self.display_image_preview(p)

    def display_image_preview(self, file_path):
        try:
            img = Image.open(file_path)
            img.thumbnail((280, 280), Image.LANCZOS)
            self.preview_image_tk = ImageTk.PhotoImage(img)
            self.image_preview_label.config(image=self.preview_image_tk, text="")
        except Exception as e:
            self.image_preview_label.config(image="", text="Preview Failed")

    def undo_last_action(self):
        if self.history_stack:
            self.redo_stack.append(self.current_image_path)
            self.load_visuals(self.history_stack.pop())
            self.update_buttons()

    def redo_last_action(self):
        if self.redo_stack:
            self.history_stack.append(self.current_image_path)
            self.load_visuals(self.redo_stack.pop())
            self.update_buttons()

    def update_buttons(self):
        self.btn_undo.config(state=tk.NORMAL if self.history_stack else tk.DISABLED)
        self.btn_redo.config(state=tk.NORMAL if self.redo_stack else tk.DISABLED)

    def copy_to_clipboard(self):
        if self.full_text_content:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.full_text_content)
            messagebox.showinfo("Copied", "All metadata copied to clipboard!")

    # ==================== METADATA DISPLAY ====================
    def display_metadata(self, file_path):
        if self.text_id: self.canvas.delete(self.text_id)
        self.map_widget.delete_all_marker()
        
        output = f"[+] Viewing: {os.path.basename(file_path)}\n{'-'*60}\n"
        
        try:
            self.current_exif_dict = piexif.load(file_path)
            def clean_val(v):
                if isinstance(v, bytes):
                    try: return v.decode('utf-8').strip().replace('\x00', '')
                    except: return f"<Binary {len(v)}>"
                return v

            for ifd_name in ["0th", "Exif"]:
                if ifd_name in self.current_exif_dict:
                    for tag_id, value in self.current_exif_dict[ifd_name].items():
                        tag_name = ExifTags.TAGS.get(tag_id, f"Unknown ({tag_id})")
                        if tag_name not in ["Padding", "MakerNote", "UserComment"]:
                            output += f"{tag_name}: {clean_val(value)}\n"

            gps_data = self.current_exif_dict.get("GPS", {})
            if gps_data:
                output += f"\n{'='*30}\n📍 GPS LOCATION FOUND:\n{'='*30}\n"
                try:
                    def get_float(t): return float(t[0]) / float(t[1])
                    if 2 in gps_data and 4 in gps_data:
                        lat = get_float(gps_data[2][0]) + get_float(gps_data[2][1])/60 + get_float(gps_data[2][2])/3600
                        lon = get_float(gps_data[4][0]) + get_float(gps_data[4][1])/60 + get_float(gps_data[4][2])/3600
                        if gps_data.get(1, b'N').decode().upper() == 'S': lat = -lat
                        if gps_data.get(3, b'E').decode().upper() == 'W': lon = -lon
                        output += f"Latitude:  {lat}\nLongitude: {lon}\n"
                        self.map_widget.set_position(lat, lon); self.map_widget.set_marker(lat, lon)
                except: pass

        except Exception as e: output += f"Error: {e}"
        
        self.full_text_content = output
        self.text_id = self.canvas.create_text(20, 20, text=output, fill=styles.COLORS["text_main"], font=styles.FONTS["code"], anchor="nw", width=900)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        
        self.canvas.tag_bind(self.text_id, "<Double-Button-1>", self.on_canvas_double_click)
        self.center_watermark() # Ensure logo is correct after load

    # ==================== DOUBLE CLICK EDIT ====================
    def on_canvas_double_click(self, event):
        try:
            canvas_x = self.canvas.canvasx(event.x)
            canvas_y = self.canvas.canvasy(event.y)
            char_index = int(self.canvas.index(self.text_id, f"@{canvas_x},{canvas_y}"))
            full_text = self.canvas.itemcget(self.text_id, "text")
            lines = full_text.split('\n')
            current_count = 0
            clicked_line = ""
            for line in lines:
                current_count += len(line) + 1
                if current_count > char_index:
                    clicked_line = line
                    break
            
            if ": " in clicked_line and "Viewing" not in clicked_line:
                tag_name, current_val = clicked_line.split(": ", 1)
                new_val = simpledialog.askstring("Quick Edit", f"Edit {tag_name}:", initialvalue=current_val, parent=self.root)
                if new_val:
                    s = filedialog.asksaveasfilename(defaultextension=".jpg", initialfile=os.path.basename(self.current_image_path).replace(".","_edited."), title="Save Edited Copy")
                    if not s: return
                    shutil.copy2(self.current_image_path, s)
                    updated = False
                    for ifd in ["0th", "Exif"]:
                        for tid, val in self.current_exif_dict.get(ifd, {}).items():
                            name = ExifTags.TAGS.get(tid, "")
                            if name == tag_name:
                                self.current_exif_dict[ifd][tid] = new_val.encode('utf-8')
                                piexif.insert(piexif.dump(self.current_exif_dict), s)
                                updated = True
                    if updated:
                        self.register_action(s)
                        messagebox.showinfo("Saved", f"Edited copy saved as:\n{os.path.basename(s)}")
                    else:
                        messagebox.showwarning("Warning", "Could not map tag name back to ID (Read-only tag?)")

        except Exception as e: print(e)

    # ==================== SCRUB ====================
    def scrub_metadata(self):
        if not self.current_image_path: return
        s = filedialog.asksaveasfilename(defaultextension=".jpg", initialfile=os.path.basename(self.current_image_path).replace(".","_cln."))
        if s: 
            try: shutil.copy2(self.current_image_path, s); piexif.remove(s); messagebox.showinfo("Success","Scrubbed!"); self.register_action(s)
            except Exception as e: messagebox.showerror("Error",f"{e}")

    def clear_map_cache(self):
        if messagebox.askyesno("Confirm", "Delete Map History?"):
            try: 
                if os.path.exists("offline_map_cache.db"): os.remove("offline_map_cache.db"); messagebox.showinfo("Done", "History deleted.")
            except: messagebox.showwarning("Error", "File in use.")

    # ==================== FAKE MENU (ADVANCED) ====================
    def open_edit_window(self):
        if not self.current_image_path: return
        win = Toplevel(self.root); win.title("Fake Metadata")
        win.geometry("500x800")
        win.configure(bg=styles.COLORS["bg_input"])

        tk.Label(win, text="Generate Fake Metadata", font=styles.FONTS["subhead"], bg=styles.COLORS["bg_input"], fg="white").pack(pady=10)
        
        current_0th = self.current_exif_dict.get("0th", {})
        def get_val(tid):
            v = current_0th.get(tid, b"")
            return v.decode() if isinstance(v, bytes) else str(v)

        entries = {}
        fields = {
            "Camera Make:": piexif.ImageIFD.Make,
            "Camera Model:": piexif.ImageIFD.Model,
            "Artist:": piexif.ImageIFD.Artist,
            "Date (Y:M:D H:M:S):": piexif.ImageIFD.DateTime
        }

        for label_text, tag_id in fields.items():
             tk.Label(win, text=label_text, bg=styles.COLORS["bg_input"], fg=styles.COLORS["text_dim"]).pack(anchor="w", padx=20)
             e = tk.Entry(win, width=50)
             val = get_val(tag_id)
             if val: e.insert(0, val)
             e.pack(pady=5)
             entries[tag_id] = e

        tk.Label(win, text="📍 Fake GPS Location", font=styles.FONTS["ui_bold"], bg=styles.COLORS["bg_input"], fg=styles.COLORS["text_main"]).pack(anchor="w", padx=20, pady=(15, 5))
        gps_frame = tk.Frame(win, bg=styles.COLORS["bg_input"]); gps_frame.pack(anchor="w", padx=20)
        tk.Label(gps_frame, text="Lat:", bg=styles.COLORS["bg_input"], fg="white").pack(side="left")
        lat_entry = tk.Entry(gps_frame, width=15); lat_entry.pack(side="left", padx=5)
        tk.Label(gps_frame, text="Lon:", bg=styles.COLORS["bg_input"], fg="white").pack(side="left")
        lon_entry = tk.Entry(gps_frame, width=15); lon_entry.pack(side="left", padx=5)

        tk.Label(win, text="➕ Custom Tags", font=styles.FONTS["ui_bold"], bg=styles.COLORS["bg_input"], fg=styles.COLORS["text_main"]).pack(anchor="w", padx=20, pady=(15, 5))
        c_frame = tk.Frame(win, bg=styles.COLORS["bg_input"]); c_frame.pack(pady=5)
        self.custom_tags_list = {}
        tag_options = ["Software", "Copyright", "ImageDescription", "LensMake", "LensModel", "BodySerialNumber", "CameraOwnerName"]
        tag_var = tk.StringVar(value="Software")
        ttk.OptionMenu(c_frame, tag_var, tag_options[0], *tag_options).pack(side="left")
        cust_e = tk.Entry(c_frame, width=30); cust_e.pack(side="left", padx=5)
        lb = tk.Listbox(win, height=4, width=50, bg="#222", fg="white", bd=0); lb.pack(pady=5)

        def add_tag():
            val = cust_e.get()
            if val: 
                self.custom_tags_list[tag_var.get()] = val
                lb.insert(tk.END, f"{tag_var.get()}: {val}")
                cust_e.delete(0,tk.END)
        tk.Button(c_frame, text="Add", command=add_tag, bg="#444", fg="white").pack(side="left")

        def save():
            s = filedialog.asksaveasfilename(defaultextension=".jpg", initialfile=os.path.basename(self.current_image_path).replace(".","_fake."))
            if s:
                try:
                    shutil.copy2(self.current_image_path, s)
                    try: ed = piexif.load(s)
                    except: ed = {"0th":{},"Exif":{},"GPS":{},"1st":{},"thumbnail":None}
                    
                    for tid, entry in entries.items():
                        if entry.get(): 
                            if tid == piexif.ImageIFD.DateTime:
                                ed["0th"][tid] = entry.get().encode('utf-8')
                                ed["Exif"][piexif.ExifIFD.DateTimeOriginal] = entry.get().encode('utf-8')
                            else:
                                ed["0th"][tid] = entry.get().encode('utf-8')

                    if lat_entry.get() and lon_entry.get():
                        def convert_to_deg(value):
                            value = float(value); abs_val = abs(value); deg = int(abs_val); t1 = (abs_val - deg) * 60; min = int(t1); sec = int(round((t1 - min) * 60 * 10000))
                            return (deg, 1), (min, 1), (sec, 10000)
                        try:
                            lat_float = float(lat_entry.get())
                            lon_float = float(lon_entry.get())
                            ed["GPS"][piexif.GPSIFD.GPSLatitudeRef] = b'N' if lat_float >= 0 else b'S'
                            ed["GPS"][piexif.GPSIFD.GPSLatitude] = convert_to_deg(lat_float)
                            ed["GPS"][piexif.GPSIFD.GPSLongitudeRef] = b'E' if lon_float >= 0 else b'W'
                            ed["GPS"][piexif.GPSIFD.GPSLongitude] = convert_to_deg(lon_float)
                        except: pass

                    for k, v in self.custom_tags_list.items():
                        vb = v.encode('utf-8')
                        if k=="Software": ed["0th"][piexif.ImageIFD.Software]=vb
                        elif k=="Copyright": ed["0th"][piexif.ImageIFD.Copyright]=vb
                        elif k=="ImageDescription": ed["0th"][piexif.ImageIFD.ImageDescription]=vb
                        elif k=="LensMake": ed["Exif"][piexif.ExifIFD.LensMake]=vb
                        elif k=="LensModel": ed["Exif"][piexif.ExifIFD.LensModel]=vb
                        elif k=="BodySerialNumber": ed["Exif"][piexif.ExifIFD.BodySerialNumber]=vb
                        elif k=="CameraOwnerName": ed["Exif"][piexif.ExifIFD.CameraOwnerName]=vb

                    piexif.insert(piexif.dump(ed), s)
                    win.destroy()
                    self.register_action(s)
                    messagebox.showinfo("Success", "Fake Metadata Applied!")
                except Exception as e: messagebox.showerror("Error", f"{e}")

        tk.Button(win, text="💾 Save", command=save, bg=styles.COLORS["btn_success"], font=styles.FONTS["ui_bold"]).pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = MetaHunterApp(root)
    root.mainloop()
