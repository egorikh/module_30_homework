from sqlalchemy import Column, String, Integer, Text

from database import Base


class Recipe(Base):
    """Модель рецепта в базе данных.

    Attributes:
        id (int): Уникальный идентификатор рецепта (первичный ключ).
        recipe_name (str): Название рецепта.
        views (int): Количество просмотров (по умолчанию 0).
        time_to_cook_in_min (int): Время приготовления в минутах.
        ingredients (str): Список ингредиентов (строка).
        description (str): Подробное описание рецепта (текст).
    """
    __tablename__ = 'recipes'
    id = Column(Integer, index=True, primary_key=True)
    recipe_name = Column(String, index=True)
    views = Column(Integer, default=0)
    time_to_cook_in_min = Column(Integer)
    ingredients = Column(String)
    description = Column(Text)
