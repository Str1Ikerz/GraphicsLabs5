import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os


class ImageProcessor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Обработка изображений - Вариант 13")
        self.root.geometry("1200x900")

        self.image1 = None  # Основное изображение (исходное)
        self.image1_transformed = None  # Основное изображение после преобразования
        self.image2 = None  # Второе изображение для наложения
        self.result_image = None  # Результат наложения

        # Для отображения в GUI
        self.photo1 = None
        self.photo1_transformed = None
        self.photo2 = None
        self.photo_result = None

        self.setup_ui()

    def setup_ui(self):
        # Главная рамка
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Панель кнопок управления
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=4, pady=10, sticky="ew")

        ttk.Button(control_frame, text="Загрузить изображение 1",
                   command=self.load_image1).grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        ttk.Button(control_frame, text="Загрузить изображение 2",
                   command=self.load_image2).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(control_frame, text="Преобразовать (увеличить красный у темных)",
                   command=self.process_brightness_transformation).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        ttk.Button(control_frame, text="Наложить (точечный свет)",
                   command=self.apply_point_light_overlay).grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        ttk.Button(control_frame, text="Сохранить результат преобразования",
                   command=self.save_transformed).grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        ttk.Button(control_frame, text="Сохранить результат наложения",
                   command=self.save_result).grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

        # Конфигурация колонок панели управления
        for i in range(4):
            control_frame.columnconfigure(i, weight=1)

        # Рамка для отображения изображений
        images_frame = ttk.Frame(main_frame)
        images_frame.grid(row=2, column=0, columnspan=4, pady=10, sticky="ew")

        # Создаем 4 области для изображений
        self.create_image_display(images_frame, 0, 0, "Исходное изображение 1", "canvas1", "size_label1")
        self.create_image_display(images_frame, 0, 1, "Результат преобразования", "canvas1_transformed",
                                  "size_label1_transformed")
        self.create_image_display(images_frame, 1, 0, "Исходное изображение 2", "canvas2", "size_label2")
        self.create_image_display(images_frame, 1, 1, "Результат наложения", "canvas_result", "size_label_result")

        # Информационная панель
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=3, column=0, columnspan=4, pady=10, sticky="ew")

        self.info_label = ttk.Label(info_frame, text="Загрузите изображения для начала работы",
                                    font=('Arial', 10))
        self.info_label.grid(row=0, column=0, pady=10)

        # Прогресс-бар
        self.progress = ttk.Progressbar(info_frame, mode='indeterminate')
        self.progress.grid(row=1, column=0, sticky="ew", pady=5)

        # Конфигурация главной сетки
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.columnconfigure(3, weight=1)

        images_frame.columnconfigure(0, weight=1)
        images_frame.columnconfigure(1, weight=1)

        info_frame.columnconfigure(0, weight=1)

    def create_image_display(self, parent, row, col, title, canvas_name, label_name):
        """Создание области для отображения изображения"""
        frame = ttk.LabelFrame(parent, text=title, padding="5")
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        # Canvas для изображения
        canvas = tk.Canvas(frame, width=280, height=200, bg='white', relief=tk.SUNKEN, bd=2)
        canvas.grid(row=0, column=0, sticky="nsew")

        # Метка для отображения размера изображения
        size_label = ttk.Label(frame, text="Размер: -", font=('Arial', 9))
        size_label.grid(row=1, column=0, pady=2)
        setattr(self, label_name, size_label)

        # Скроллбары
        h_scroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=canvas.xview)
        h_scroll.grid(row=2, column=0, sticky="ew")
        canvas.configure(xscrollcommand=h_scroll.set)

        v_scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        v_scroll.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=v_scroll.set)

        # Сохраняем ссылку на canvas
        setattr(self, canvas_name, canvas)

        # Конфигурация сетки
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        # Родительская сетка
        parent.rowconfigure(row, weight=1)
        parent.columnconfigure(col, weight=1)

    def numpy_to_photoimage(self, np_array, max_size=(280, 200)):
        """Преобразование numpy массива в PhotoImage для отображения в tkinter"""
        if np_array is None:
            return None

        # Убеждаемся, что значения в правильном диапазоне
        if np_array.dtype != np.uint8:
            np_array = np.clip(np_array, 0, 255).astype(np.uint8)

        # Создаем PIL изображение
        pil_image = Image.fromarray(np_array)

        # Масштабируем для отображения, сохраняя пропорции
        pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Преобразуем в PhotoImage
        return ImageTk.PhotoImage(pil_image)

    def update_image_display(self, canvas, photo_image, np_array=None, size_label=None):
        """Обновление отображения изображения на canvas"""
        canvas.delete("all")

        if photo_image is not None:
            # Центрируем изображение
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()

            if canvas_width <= 1:  # Canvas еще не отрисован
                canvas_width = 280
                canvas_height = 200

            img_width = photo_image.width()
            img_height = photo_image.height()

            x = max(0, (canvas_width - img_width) // 2)
            y = max(0, (canvas_height - img_height) // 2)

            canvas.create_image(x, y, anchor=tk.NW, image=photo_image)

            # Обновляем область прокрутки
            canvas.configure(scrollregion=canvas.bbox("all"))

            # Обновляем информацию о размере
            if np_array is not None and size_label is not None:
                size_label.config(text=f"Размер: {np_array.shape[1]}x{np_array.shape[0]}")

    def load_image1(self):
        """Загрузка основного изображения"""
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
                self.image1_transformed = None  # Сбрасываем преобразованное изображение

                # Обновляем отображение
                self.photo1 = self.numpy_to_photoimage(self.image1)
                self.update_image_display(self.canvas1, self.photo1, self.image1, self.size_label1)

                # Очищаем canvas преобразованного изображения
                self.canvas1_transformed.delete("all")
                self.photo1_transformed = None
                self.size_label1_transformed.config(text="Размер: -")

                self.info_label.config(text=f"Изображение 1 загружено: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{str(e)}")

    def load_image2(self):
        """Загрузка второго изображения"""
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

                # Обновляем отображение
                self.photo2 = self.numpy_to_photoimage(self.image2)
                self.update_image_display(self.canvas2, self.photo2, self.image2, self.size_label2)

                self.info_label.config(text=f"Изображение 2 загружено: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{str(e)}")

    def read_image(self, filepath):
        """Чтение изображения и преобразование в numpy массив RGB"""
        img = Image.open(filepath)

        # Преобразуем в RGB если необходимо
        if img.mode != 'RGB':
            img = img.convert('RGB')

        return np.array(img)

    def get_pixel_brightness_simple(self, pixel):
        """Простое вычисление яркости пикселя (максимальное значение RGB)"""
        return max(pixel) / 255.0

    def increase_red_for_dark_pixels(self, rgb_array, brightness_threshold=0.25):
        """
        Увеличение красного компонента у темных пикселей (яркость < 25%)
        Красный канал увеличивается на 100% (но не более 255)
        """
        result = rgb_array.copy().astype(np.float32)

        # Обрабатываем каждый пиксель
        for y in range(rgb_array.shape[0]):
            for x in range(rgb_array.shape[1]):
                pixel = rgb_array[y, x]

                # Вычисляем яркость как максимум из RGB компонент
                brightness = self.get_pixel_brightness_simple(pixel)

                # Если яркость меньше порога, увеличиваем красный канал
                if brightness < brightness_threshold:
                    # Увеличиваем красный канал на 100%
                    new_red = min(pixel[0] * 2, 255)
                    result[y, x, 0] = new_red
                    # Зеленый и синий каналы остаются без изменений
                    result[y, x, 1] = pixel[1]
                    result[y, x, 2] = pixel[2]

        return result.astype(np.uint8)

    def apply_point_light_blend(self, bottom_layer, top_layer):
        """
        Наложение изображений по правилу "точечный свет":
        - Если яркость пикселя верхнего слоя < 50% - берем минимум по каналам (затемнение)
        - Иначе - берем максимум по каналам (осветление)
        """
        # Приводим изображения к одному размеру
        min_height = min(bottom_layer.shape[0], top_layer.shape[0])
        min_width = min(bottom_layer.shape[1], top_layer.shape[1])

        bottom_resized = bottom_layer[:min_height, :min_width]
        top_resized = top_layer[:min_height, :min_width]

        result = np.zeros_like(bottom_resized)

        # Обрабатываем каждый пиксель
        for y in range(min_height):
            for x in range(min_width):
                top_pixel = top_resized[y, x]
                bottom_pixel = bottom_resized[y, x]
                top_brightness = self.get_pixel_brightness_simple(top_pixel)

                if top_brightness < 0.5:
                    # Затемнение - берем минимум по каждому каналу
                    result[y, x] = np.minimum(bottom_pixel, top_pixel)
                else:
                    # Осветление - берем максимум по каждому каналу
                    result[y, x] = np.maximum(bottom_pixel, top_pixel)

        return result

    def process_brightness_transformation(self):
        """Выполнение преобразования основного изображения"""
        if self.image1 is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение 1")
            return

        try:
            self.progress.start()

            # Применяем преобразование
            self.image1_transformed = self.increase_red_for_dark_pixels(self.image1, 0.25)

            # Обновляем отображение преобразованного изображения
            self.photo1_transformed = self.numpy_to_photoimage(self.image1_transformed)
            self.update_image_display(self.canvas1_transformed, self.photo1_transformed,
                                      self.image1_transformed, self.size_label1_transformed)

            self.progress.stop()
            self.info_label.config(text="Преобразование выполнено: красный компонент увеличен у точек с яркостью < 25%")
            messagebox.showinfo("Успех", "Преобразование изображения 1 завершено")

        except Exception as e:
            self.progress.stop()
            messagebox.showerror("Ошибка", f"Ошибка при преобразовании:\n{str(e)}")

    def apply_point_light_overlay(self):
        """Применение наложения по правилу точечного света"""
        if self.image1 is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение 1")
            return

        if self.image2 is None:
            messagebox.showwarning("Предупреждение", "Загрузите изображение 2")
            return

        try:
            self.progress.start()

            # Используем преобразованное изображение, если оно есть, иначе исходное
            base_image = self.image1_transformed if self.image1_transformed is not None else self.image1

            # Применяем наложение
            self.result_image = self.apply_point_light_blend(base_image, self.image2)

            # Обновляем отображение результата
            self.photo_result = self.numpy_to_photoimage(self.result_image)
            self.update_image_display(self.canvas_result, self.photo_result,
                                      self.result_image, self.size_label_result)

            self.progress.stop()
            self.info_label.config(text="Наложение по правилу 'точечный свет' выполнено")
            messagebox.showinfo("Успех", "Наложение изображений по правилу 'точечный свет' завершено")

        except Exception as e:
            self.progress.stop()
            messagebox.showerror("Ошибка", f"Ошибка при наложении:\n{str(e)}")

    def save_transformed(self):
        """Сохранение преобразованного изображения"""
        if self.image1_transformed is None:
            messagebox.showwarning("Предупреждение", "Сначала выполните преобразование изображения")
            return

        filename = filedialog.asksaveasfilename(
            title="Сохранить преобразованное изображение",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ],
            initialfile="transformed_image.png"
        )

        if not filename:
            return

        try:
            self.save_image(self.image1_transformed, filename)
            self.info_label.config(text=f"Преобразованное изображение сохранено: {filename}")
            messagebox.showinfo("Успех", f"Преобразованное изображение сохранено:\n{filename}")
        except Exception as e:
            error_msg = f"Ошибка при сохранении файла:\n{str(e)}"
            self.info_label.config(text="Ошибка сохранения файла")
            messagebox.showerror("Ошибка", error_msg)

    def save_result(self):
        """Сохранение результата наложения"""
        if self.result_image is None:
            messagebox.showwarning("Предупреждение", "Сначала выполните наложение изображений")
            return

        filename = filedialog.asksaveasfilename(
            title="Сохранить результат наложения",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ],
            initialfile="result_image.png"
        )

        if not filename:
            return

        try:
            self.save_image(self.result_image, filename)
            self.info_label.config(text=f"Результат наложения сохранен: {filename}")
            messagebox.showinfo("Успех", f"Результат наложения сохранен:\n{filename}")
        except Exception as e:
            error_msg = f"Ошибка при сохранении файла:\n{str(e)}"
            self.info_label.config(text="Ошибка сохранения файла")
            messagebox.showerror("Ошибка", error_msg)

    def save_image(self, image_array, filename):
        """Сохранение изображения в файл"""
        img = Image.fromarray(image_array)
        img.save(filename)

    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


if __name__ == "__main__":
    app = ImageProcessor()
    app.run()

