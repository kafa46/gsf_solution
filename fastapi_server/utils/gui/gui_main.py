import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
from func import detect_stickers

class StickerDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sticker Detection")
        
        self.zoom_mode = 0  # 0: 비활성화, 1: 확대모드, 2: 축소모드
        self.zoom_percent = 100  # 초기 확대/축소 비율
        self.pen_active = False  # 펜 모드 활성화 여부
        self.magnifier_active = False  # 돋보기 모드 활성화 여부

        self.create_widgets()
        self.bind_events()


    def create_widgets(self):
        """GUI 위젯을 생성하고 배치."""
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        self.create_tool_frame()
        self.create_magnifier_frame()
        self.create_range_frames()
        self.create_canvas()
        self.create_menu()


    def create_tool_frame(self):
        """도구 관련 프레임과 위젯 생성."""
        self.tool_frame = tk.Frame(self.main_frame)
        self.tool_frame.pack(side="top", fill="x")

        self.pen_icon = self.load_image("./gui_img/pen.png", 20, 20)
        self.pen_button = tk.Button(self.tool_frame, image=self.pen_icon, command=self.toggle_pen_mode)
        self.pen_button.pack(side="left", padx=5, pady=5)
        
        self.pen_mode_label = tk.Label(self.tool_frame, text="(기본모드)")
        self.pen_mode_label.pack(side="left", padx=5, pady=5)

        self.rgb_label = tk.Label(self.tool_frame, text="HSV: N/A")
        self.rgb_label.pack(side="left", padx=5, pady=5)

        self.explan = tk.Label(self.tool_frame, text="*값의 범위는 넉넉하게 주시는게 좋습니다.")
        self.explan.pack(side="left", padx=5, pady=5)


    def create_magnifier_frame(self):
        """돋보기 관련 프레임과 위젯 생성."""
        self.magnifier_frame = tk.Frame(self.main_frame)
        self.magnifier_frame.pack(side="top", fill="x")

        self.magnifier_icon = self.load_image("./gui_img/magnifier.png", 20, 20)
        self.magnifier_button = tk.Button(self.magnifier_frame, image=self.magnifier_icon, command=self.toggle_magnifier_mode)
        self.magnifier_button.pack(side="left", padx=5, pady=5)

        self.zoom_mode_label = tk.Label(self.magnifier_frame, text="(기본모드)")
        self.zoom_mode_label.pack(side="left", padx=5, pady=5)

        self.zoom_label = tk.Label(self.magnifier_frame, text="Zoom: 100% (origin)")
        self.zoom_label.pack(side="left", padx=5, pady=5)


    def create_range_frames(self):
        """범위 및 마진 입력 필드 생성."""
        self.range_frame = tk.Frame(self.main_frame)
        self.range_frame.pack(side="top", fill="x")

        self.lower_label = tk.Label(self.range_frame, text="Lower Bound (H,S,V):")
        self.lower_label.pack(side="left", padx=5, pady=5)
        self.lower_entry = tk.Entry(self.range_frame)
        self.lower_entry.pack(side="left", padx=5, pady=5)

        self.upper_label = tk.Label(self.range_frame, text="Upper Bound (H,S,V):")
        self.upper_label.pack(side="left", padx=5, pady=5)
        self.upper_entry = tk.Entry(self.range_frame)
        self.upper_entry.pack(side="left", padx=5, pady=5)

        self.range_frame2 = tk.Frame(self.main_frame)
        self.range_frame2.pack(side="top", fill="x")

        self.margin_label = tk.Label(self.range_frame2, text="Margin:")
        self.margin_label.pack(side="left", padx=5, pady=5)
        self.margin_entry = tk.Entry(self.range_frame2)
        self.margin_entry.pack(side="left", padx=5, pady=5)
        self.margin_entry.insert(0, "10")  # 기본값 10

        self.detect_button = tk.Button(self.range_frame2, text="Detect Stickers", command=self.detect_stickers, state="disabled")
        self.detect_button.pack(side="left", padx=5, pady=5)
    
    """ 펜 관련 기능 함수 """
    def toggle_pen_mode(self):
        """펜 모드 활성화/비활성화."""
        self.pen_active = not self.pen_active
        self.pen_button.config(relief="sunken" if self.pen_active else "raised")
        self.magnifier_active = False  # 펜 모드에서는 돋보기 모드 비활성화
        self.update_cursor()
        
    """ 돋보기 관련 """
    
    def create_canvas(self):
        """이미지를 표시할 캔버스 생성."""
        self.canvas = tk.Canvas(self.main_frame, cursor="cross")
        self.canvas.pack(fill="both", expand=True)

    def create_menu(self):
        """메뉴 생성."""
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open", command=self.open_image)
        self.file_menu.add_command(label="Save", command=self.save_image, state="disabled")

    def bind_events(self):
        """이벤트 바인딩."""
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<Button-1>", self.get_hsv_value)  # HSV 값을 얻기 위한 클릭 이벤트 바인딩
        self.canvas.bind("<Button-1>", self.on_magnifier_click, add="+")

    def load_image(self, path, width, height):
        """이미지를 로드하고 크기를 조정하여 반환."""
        image = Image.open(path).resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(image)



    def toggle_magnifier_mode(self):
        """돋보기 모드 활성화/비활성화 및 모드 전환."""
        self.zoom_mode = (self.zoom_mode + 1) % 3
        self.magnifier_active = self.zoom_mode != 0
        self.update_cursor()
        self.update_zoom_mode_label()

    def update_cursor(self):
        """캔버스의 커서를 현재 모드에 맞게 업데이트."""
        if self.pen_active:
            self.canvas.config(cursor="pencil")
        elif self.magnifier_active:
            self.canvas.config(cursor="plus")
        else:
            self.canvas.config(cursor="cross")

    def update_zoom_mode_label(self):
        """줌 모드 라벨을 업데이트."""
        modes = ["(기본모드)", "(확대모드)", "(축소모드)"]
        self.zoom_mode_label.config(text=modes[self.zoom_mode])

    def open_image(self):
        """이미지를 열고 캔버스에 표시."""
        self.image_path = filedialog.askopenfilename()
        if self.image_path:
            try:
                self.image = Image.open(self.image_path).resize((800, 800), Image.LANCZOS)
                self.original_image = self.image.copy()
                self.update_canvas_image(self.image)
                self.root.geometry("800x900")
                self.enable_image_actions()
            except Exception as e:
                print(f"Error loading image: {e}")

    def enable_image_actions(self):
        """이미지와 관련된 액션을 활성화."""
        self.file_menu.entryconfig("Save", state="normal")
        self.detect_button.config(state="normal")
        self.pen_button.config(state="normal")

    def save_image(self):
        """결과 이미지를 저장."""
        if self.result_image is not None:
            save_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                     filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")])
            if save_path:
                cv2.imwrite(save_path, self.result_image)
                print(f"Image saved to {save_path}")

    def on_button_press(self, event):
        """마우스 버튼을 누를 때의 이벤트 처리."""
        if self.pen_active:
            self.get_hsv_value(event)

    def get_hsv_value(self, event):
        """클릭한 지점의 HSV 값을 가져와 표시."""
        if self.image and self.pen_active:
            x, y = event.x, event.y
            rgb = self.image.getpixel((x, y))
            hsv = cv2.cvtColor(np.array([[rgb]], dtype=np.uint8), cv2.COLOR_RGB2HSV)[0][0]
           
            self.rgb_label.config(text=f"HSV: {hsv}")

    def detect_stickers(self):
        """범위 입력 값에 따라 스티커를 탐지하고 결과를 표시."""
        if self.image_path:
            lower_bound = self.parse_hsv_values(self.lower_entry.get())
            upper_bound = self.parse_hsv_values(self.upper_entry.get())
            margin = int(self.margin_entry.get())

            self.result_image = detect_stickers(self.image_path, lower_bound, upper_bound, margin)
            self.show_image(self.result_image)
            self.detect_button.config(text="Show Original Image", command=self.show_original_image)

    def parse_hsv_values(self, hsv_string):
        """HSV 문자열을 배열로 변환."""
        return np.array(list(map(int, hsv_string.split(','))))

    def apply_zoom(self, image_mouse_x, image_mouse_y):
        """이미지의 확대/축소를 적용하고 캔버스에 반영."""
        new_size = (
            int(self.original_image.width * self.zoom_percent / 100),
            int(self.original_image.height * self.zoom_percent / 100)
        )
        resized_image = self.original_image.resize(new_size, Image.LANCZOS)

        new_canvas_mouse_x = image_mouse_x * new_size[0] / self.original_image.width
        new_canvas_mouse_y = image_mouse_y * new_size[1] / self.original_image.height

        self.update_canvas_image(resized_image)

        self.canvas.xview_moveto(new_canvas_mouse_x / new_size[0])
        self.canvas.yview_moveto(new_canvas_mouse_y / new_size[1])

        self.update_zoom_label()

    def update_zoom_label(self):
        """현재 줌 상태를 표시하는 라벨을 업데이트."""
        zoom_text = f"Zoom: {self.zoom_percent}%"
        if self.zoom_percent == 100:
            zoom_text += " (origin)"
        self.zoom_label.config(text=zoom_text)

    def update_canvas_image(self, image):
        """캔버스에 이미지를 업데이트하여 표시."""
        self.tk_image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def show_image(self, image_cv):
        """OpenCV 이미지를 PIL 이미지로 변환하여 캔버스에 표시."""
        result_image_rgb = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
        result_image_pil = Image.fromarray(result_image_rgb)
        self.update_canvas_image(result_image_pil)

    def show_original_image(self):
        """원본 이미지를 캔버스에 표시."""
        self.update_canvas_image(self.original_image)
        self.detect_button.config(text="Detect Stickers", command=self.detect_stickers)

    def on_magnifier_click(self, event):
        """돋보기 모드에서 클릭 시 확대/축소 기능을 처리."""
        if self.magnifier_active:
            canvas_mouse_x = self.canvas.canvasx(event.x)
            canvas_mouse_y = self.canvas.canvasy(event.y)
            image_mouse_x = canvas_mouse_x / self.zoom_percent * 100
            image_mouse_y = canvas_mouse_y / self.zoom_percent * 100

            if self.zoom_mode == 1:  # 확대모드
                self.zoom_percent = min(self.zoom_percent + 5, 500)  # 최대 확대 비율 500%
            elif self.zoom_mode == 2:  # 축소모드
                self.zoom_percent = max(self.zoom_percent - 5, 10)  # 최소 축소 비율 10%

            self.apply_zoom(image_mouse_x, image_mouse_y)


if __name__ == "__main__":
    root = tk.Tk()
    app = StickerDetectionApp(root)
    root.mainloop()
