import customtkinter

def configure_theme(root):
    """Настраивает темную тему приложения."""
    customtkinter.set_appearance_mode("dark")  # Темный режим
    customtkinter.set_default_color_theme("dark-blue")  # Цветовая тема
    root.configure(bg="#2d2d2e")  # Устанавливаем темный фон для корневого окна

def create_rounded_entry(parent, placeholder="Введите текст", show=None):
    """Создает поле ввода с закругленными углами."""
    return customtkinter.CTkEntry(
        parent,
        width=300,
        height=35,
        corner_radius=10,
        placeholder_text=placeholder,
        show=show
    )

def create_rounded_button(parent, text, command):
    """Создает кнопку с закругленными углами."""
    return customtkinter.CTkButton(
        parent,
        text=text,
        command=command,
        width=200,
        height=40,
        corner_radius=10
    )

def create_rounded_label(parent, text):
    """Создает текстовую метку с темной темой."""
    return customtkinter.CTkLabel(
        parent,
        text=text,
        text_color="white",  # Белый цвет текста
    )

    

