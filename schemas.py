from pydantic import BaseModel, Field


class BaseRecipe(BaseModel):
    """Базовая схема рецепта (общие поля).

    Attributes:
        recipe_name (str): Название рецепта.
        time_to_cook_in_min (int): Время приготовления (мин).
    """
    recipe_name: str = Field(..., min_length=1)
    time_to_cook_in_min: int = Field(..., gt=0)


class RecipeIn(BaseRecipe):
    """Схема для создания рецепта (входные данные)."""
    ingredients: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)


class RecipesOut(BaseRecipe):
    """Схема для вывода краткой информации о рецепте.

    Attributes:
        views (int): Количество просмотров.
    """
    id: int
    views: int

    class Config:
        from_attributes = True


class RecipeInfoOut(BaseRecipe):
    """Схема для вывода полной информации о рецепте.

    Attributes:
        ingredients (str): Список ингредиентов.
        description (str): Описание рецепта.
    """
    id: int
    views: int
    ingredients: str
    description: str

    class Config:
        from_attributes = True
