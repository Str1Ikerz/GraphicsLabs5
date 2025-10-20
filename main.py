import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import math


class ImageProcessor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Обработка изображений")
        self.root.geometry("1200x900")

        self.image1 = None
        self.image1_transformed = None
        self.image2 = None
        self.result_image = None

        self.photo1 = None
        self.photo1_transformed = None
        self.photo2 = None
        self.photo_result = None

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, columnspan=4, pady=10, sticky="ew")

        ttk.Button(control_frame, text="Загрузить изображение 1",
                   command=self.load_image1).grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        ttk.Button(control_frame, text="Загрузить изображение 2",
                   command=self.load_image2).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(control_frame, text="Преобразовать (синус тона)",
                   command=self.process_sine_transformation).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        ttk.Button(control_frame, text="Наложить (мягкий свет)",
                   command=self.apply_soft_light_overlay).grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        ttk.Button(control_frame, text="Сохранить в PPM",
                   command=self.save_ppm).grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        ttk.Button(control_frame, text="Сохранить в PBM",
                   command=self.save_pbm).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(control_frame, text="Сохранить оба формата",
                   command=self.save_both_formats).grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

        for i in range(4):
            control_frame.columnconfigure(i, weight=1)

        images_frame = ttk.Frame(main_frame)
        images_frame.grid(row=1, column=0, columnspan=4, pady=10, sticky="ew")

        self.create_image_display(images_frame, 0, 0, "Исходное изображение 1", "canvas1")
        self.create_image_display(images_frame, 0, 1, "Результат преобразования", "canvas1_transformed")
        self.create_image_display(images_frame, 1, 0, "Исходное изображение 2", "canvas2")
        self.create_image_display(images_frame, 1, 1, "Результат наложения", "canvas_result")

        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=2, column=0, columnspan=4, pady=10, sticky="ew")

        self.info_label = ttk.Label(info_frame, text="Загрузите изображения для начала работы",
                                    font=('Arial', 10))
        self.info_label.grid(row=0, column=0, pady=10)

        self.progress = ttk.Progressbar(info_frame, mode='indeterminate')
        self.progress.grid(row=1, column=0, sticky="ew", pady=5)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.columnconfigure(3, weight=1)

        images_frame.columnconfigure(0, weight=1)
        images_frame.columnconfigure(1, weight=1)

        info_frame.columnconfigure(0, weight=1)

    def create_image_display(self, parent, row, col, title, canvas_name):
        frame = ttk.LabelFrame(parent, text=title, padding="5")
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        canvas = tk.Canvas(frame, width=280, height=200, bg='white', relief=tk.SUNKEN, bd=2)
        canvas.grid(row=0, column=0, sticky="nsew")

        h_scroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=canvas.xview)
        h_scroll.grid(row=1, column=0, sticky="ew")
        canvas.configure(xscrollcommand=h_scroll.set)

        v_scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        v_scroll.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=v_scroll.set)

        setattr(self, canvas_name, canvas)

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        parent.rowconfigure(row, weight=1)
        parent.columnconfigure(col, weight=1)

    def numpy_to_photoimage(self, np_array, max_size=(280, 200)):
        if np_array is None:
            return None

        if np_array.dtype != np.uint8:
            np_array = np.clip(np_array, 0, 255).astype(np.uint8)

        pil_image = Image.fromarray(np_array)
        pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(pil_image)

    def update_image_display(self, canvas, photo_image, np_array=None):
        canvas.delete("all")

        if photo_image is not None:
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()

            if canvas_width <= 1:
                canvas_width = 280
                canvas_height = 200

            img_width = photo_image.width()
            img_height = photo_image.height()

            x = max(0, (canvas_width - img_width) // 2)
            y = max(0, (canvas_height - img_height) // 2)

            canvas.create_image(x, y, anchor=tk.NW, image=photo_image)
            canvas.configure(scrollregion=canvas.bbox("all"))

            if np_array is not None:
                info_text = f"{np_array.shape[1]}x{np_array.shape[0]}"
                canvas.create_text(10, 10, anchor=tk.NW, text=info_text,
                                   fill="red", font=('Arial', 9, 'bold'))

    def load_image1(self):
        filename = filedialog.askopenfilename(
            title="Выберите изображение 1",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif"),
                ("All files", "*.*")
            ]
        )

        if filename:
            try:
                self.image1 = self.read_image(filename)
                self.image1_transformed = None

                self.photo1 = self.numpy_to_photoimage(self.image1)
                self.update_image_display(self.canvas1, self.photo1, self.image1)

                self.canvas1_transformed.delete("all")
                self.photo1_transformed = None

                self.info_label.config(text=f"Изображение 1 загружено: {os.path.basename(filename)} "
                                            f"({self.image1.shape[1]}x{self.image1.shape[0]})")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{str(e)}")

    def load_image2(self):
        filename = filedialog.askopenfilename(
            title="Выберите изображение 2",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif"),
                ("All files", "*.*")
            ]
        )

        if filename:
            try:
                self.image2 = self.read_image(filename)

                self.photo2 = self.numpy_to_photoimage(self.image2)
                self.update_image_display(self.canvas2, self.photo2, self.image2)

                self.info_label.config(text=f"Изображение 2 загружено: {os.path.basename(filename)} "
                                            f"({self.image2.shape[1]}x{self.image2.shape[0]})")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{str(e)}")

    def read_image(self, filepath):
        img = Image.open(filepath)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        return np.array(img)

    def rgb_to_hsv(self, rgb_array):
        rgb_normalized = rgb_array.astype(np.float32) / 255.0
        r, g, b = rgb_normalized[:,:,0], rgb_normalized[:,:,1], rgb_normalized[:,:,2]
        
        max_val = np.max(rgb_normalized, axis=2)
        min_val = np.min(rgb_normalized, axis=2)
        diff = max_val - min_val
        
        h = np.zeros_like(max_val)
        s = np.zeros_like(max_val)
        v = max_val
        
        # Calculate hue
        mask = diff != 0
        r_mask = (max_val == r) & mask
        g_mask = (max_val == g) & mask
        b_mask = (max_val == b) & mask
        
        h[r_mask] = 60 * ((g[r_mask] - b[r_mask]) / diff[r_mask] % 6)
        h[g_mask] = 60 * ((b[g_mask] - r[g_mask]) / diff[g_mask] + 2)
        h[b_mask] = 60 * ((r[b_mask] - g[b_mask]) / diff[b_mask] + 4)
        
        # Calculate saturation
        s[mask] = diff[mask] / max_val[mask]
        
        return np.stack([h, s, v], axis=2)

    def hsv_to_rgb(self, hsv_array):
        h, s, v = hsv_array[:,:,0], hsv_array[:,:,1], hsv_array[:,:,2]
        
        c = v * s
        x = c * (1 - np.abs((h / 60) % 2 - 1))
        m = v - c
        
        r_prime = np.zeros_like(h)
        g_prime = np.zeros_like(h)
        b_prime = np.zeros_like(h)
        
        mask = (h >= 0) & (h < 60)
        r_prime[mask], g_prime[mask], b_prime[mask] = c[mask], x[mask], 0
        
        mask = (h >= 60) & (h < 120)
        r_prime[mask], g_prime[mask], b_prime[mask] = x[mask], c[mask], 0
        
        mask = (h >= 120) & (h < 180)
        r_prime[mask], g_prime[mask], b_prime[mask] = 0, c[mask], x[mask]
        
        mask = (h >= 180) & (h < 240)
        r_prime[mask], g_prime[mask], b_prime[mask] = 0, x[mask], c[mask]
        
        mask = (h >= 240) & (h < 300)
        r_prime[mask], g_prime[mask], b_prime[mask] = x[mask], 0, c[mask]
        
        mask = (h >= 300) & (h < 360)
        r_prime[mask], g_prime[mask], b_prime[mask] = c[mask], 0, x[mask]
        
        r = (r_prime + m) * 255
        g = (g_prime + m) * 255
        b = (b_prime + m) * 255
        
        return np.stack([r, g, b], axis=2).astype(np.uint8)

    def apply_sine_to_saturation(self, rgb_array, frequency=8, amplitude=0.5):
        hsv = self.rgb_to_hsv(rgb_array)
        height, width = hsv.shape[:2]
        
        for y in range(height):
            for x in range(width):
                tone = (x + y) / (width + height) * frequency * 2 * math.pi
                sine_value = math.sin(tone) * amplitude + 0.5
                hsv[y, x, 1] = np.clip(sine_value, 0, 1)
        
        return self.hsv_to_rgb(hsv)

    def apply_soft_light_blend(self, bottom_layer, top_layer):
        min_height = min(bottom_layer.shape[0], top_layer.shape[0])
        min_width = min(bottom_layer.shape[1], top_layer.shape[1])

        bottom_resized = bottom_layer[:min_height, :min_width].astype(np.float32) / 255.0
        top_resized = top_layer[:min_height, :min_width].astype(np.float32) / 255.0

        result = np.zeros_like(bottom_resized)

        for y in range(min_height):
            for x in range(min_width):
                for c in range(3):
                    bottom_val = bottom_resized[y, x, c]
                    top_val = top_resized[y, x, c]
                    
                    if top_val <= 0.5:
                        result_val = bottom_val - (1 - 2 * top_val) * bottom_val * (1 - bottom_val)
                    else:
                        result_val = bottom_val + (2 * top_val - 1) * (self.gamma_correction(bottom_val) - bottom_val)
                    
                    result[y, x, c] = np.clip(result_val, 0, 1)

        return (result * 255).astype(np.uint8)

    def gamma_correction(self, value, gamma=2.2):
        return value ** (1/gamma)

    def process_sine_transformation(self):
        if self.image1 is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение 1")
            return

        try:
            self.progress.start()
            self.image1_transformed = self.apply_sine_to_saturation(self.image1)
            self.photo1_transformed = self.numpy_to_photoimage(self.image1_transformed)
            self.update_image_display(self.canvas1_transformed, self.photo1_transformed, self.image1_transformed)

            self.progress.stop()
            self.info_label.config(text="Преобразование выполнено: синус тона применен к каналу насыщенности")
            messagebox.showinfo("Успех", "Преобразование изображения 1 завершено")

        except Exception as e:
            self.progress.stop()
            messagebox.showerror("Ошибка", f"Ошибка при преобразовании:\n{str(e)}")

    def apply_soft_light_overlay(self):
        if self.image1 is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение 1")
            return

        if self.image2 is None:
            messagebox.showwarning("Предупреждение", "Загрузите изображение 2")
            return

        try:
            self.progress.start()
            base_image = self.image1_transformed if self.image1_transformed is not None else self.image1
            self.result_image = self.apply_soft_light_blend(base_image, self.image2)
            self.photo_result = self.numpy_to_photoimage(self.result_image)
            self.update_image_display(self.canvas_result, self.photo_result, self.result_image)

            self.progress.stop()
            self.info_label.config(text=f"Наложение выполнено. Размер результата: "
                                        f"{self.result_image.shape[1]}x{self.result_image.shape[0]}")
            messagebox.showinfo("Успех", "Наложение изображений по правилу 'мягкий свет' завершено")

        except Exception as e:
            self.progress.stop()
            messagebox.showerror("Ошибка", f"Ошибка при наложении:\n{str(e)}")

    def save_ppm(self):
        if self.result_image is None:
            messagebox.showwarning("Предупреждение",
                                   "Сначала выполните преобразование и наложение изображений")
            return

        filename = filedialog.asksaveasfilename(
            title="Сохранить изображение в PPM (P3)",
            defaultextension=".ppm",
            filetypes=[
                ("PPM files (*.ppm)", "*.ppm"),
                ("All files (*.*)", "*.*")
            ],
            initialfile="processed_image.ppm"
        )

        if not filename:
            return

        try:
            self.progress.start()
            self.write_ppm_file(filename)
            self.progress.stop()

            self.info_label.config(text=f"Изображение успешно сохранено в PPM: {filename}")
            messagebox.showinfo("Успех", f"Изображение сохранено в формате PPM (P3):\n{filename}")
        except Exception as e:
            self.progress.stop()
            error_msg = f"Ошибка при сохранении файла:\n{str(e)}"
            self.info_label.config(text="Ошибка сохранения файла")
            messagebox.showerror("Ошибка", error_msg)

    def save_pbm(self):
        if self.result_image is None:
            messagebox.showwarning("Предупреждение",
                                   "Сначала выполните преобразование и наложение изображений")
            return

        filename = filedialog.asksaveasfilename(
            title="Сохранить изображение в PBM (P1)",
            defaultextension=".pbm",
            filetypes=[
                ("PBM files (*.pbm)", "*.pbm"),
                ("All files (*.*)", "*.*")
            ],
            initialfile="processed_image.pbm"
        )

        if not filename:
            return

        try:
            self.progress.start()
            self.write_pbm_file(filename)
            self.progress.stop()

            self.info_label.config(text=f"Изображение успешно сохранено в PBM: {filename}")
            messagebox.showinfo("Успех", f"Изображение сохранено в формате PBM (P1):\n{filename}")
        except Exception as e:
            self.progress.stop()
            error_msg = f"Ошибка при сохранении файла:\n{str(e)}"
            self.info_label.config(text="Ошибка сохранения файла")
            messagebox.showerror("Ошибка", error_msg)

    def save_both_formats(self):
        if self.result_image is None:
            messagebox.showwarning("Предупреждение",
                                   "Сначала выполните преобразование и наложение изображений")
            return

        base_filename = filedialog.asksaveasfilename(
            title="Сохранить изображение в обоих форматах",
            defaultextension=".ppm",
            filetypes=[
                ("PPM files (*.ppm)", "*.ppm"),
                ("All files (*.*)", "*.*")
            ],
            initialfile="processed_image"
        )

        if not base_filename:
            return

        try:
            self.progress.start()
            base_name = os.path.splitext(base_filename)[0]
            
            ppm_filename = base_name + ".ppm"
            pbm_filename = base_name + ".pbm"
            
            self.write_ppm_file(ppm_filename)
            self.write_pbm_file(pbm_filename)
            self.progress.stop()

            self.info_label.config(text=f"Изображения сохранены в PPM и PBM форматах")
            messagebox.showinfo("Успех", f"Изображения сохранены:\nPPM: {ppm_filename}\nPBM: {pbm_filename}")
        except Exception as e:
            self.progress.stop()
            error_msg = f"Ошибка при сохранении файлов:\n{str(e)}"
            self.info_label.config(text="Ошибка сохранения файлов")
            messagebox.showerror("Ошибка", error_msg)

    def write_ppm_file(self, filename):
        if self.result_image is None:
            raise ValueError("Нет данных изображения для сохранения")

        height, width = self.result_image.shape[:2]

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("P3\n")
            f.write("# Обработанное изображение\n")
            f.write(f"# Размер изображения: {width} x {height}\n")
            f.write("# Максимальное значение цвета: 255\n")
            f.write("# Преобразование: синус тона в канале насыщенности\n")
            f.write("# Наложение: мягкий свет\n")
            f.write(f"{width} {height}\n")
            f.write("255\n")

            for y in range(height):
                row = self.result_image[y]
                rgb_strings = [f"{int(pixel[0])} {int(pixel[1])} {int(pixel[2])}" for pixel in row]
                f.write(" ".join(rgb_strings) + "\n")

    def write_pbm_file(self, filename):
        if self.result_image is None:
            raise ValueError("Нет данных изображения для сохранения")

        height, width = self.result_image.shape[:2]

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("P1\n")
            f.write("# Обработанное изображение\n")
            f.write(f"# Размер изображения: {width} x {height}\n")
            f.write("# Преобразование: синус тона в канале насыщенности\n")
            f.write("# Наложение: мягкий свет\n")
            f.write(f"{width} {height}\n")

            for y in range(height):
                row = self.result_image[y]
                pbm_row = []
                for pixel in row:
                    brightness = np.mean(pixel) / 255.0
                    if brightness > 0.5:
                        pbm_row.append('0')
                    else:
                        pbm_row.append('1')
                f.write(" ".join(pbm_row) + "\n")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ImageProcessor()
    app.run()
