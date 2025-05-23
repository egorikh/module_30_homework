from contextlib import asynccontextmanager
from typing import List

from database import engine, session
from fastapi import FastAPI, HTTPException
from sqlalchemy import asc, desc
from sqlalchemy.future import select


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения.

    - Создает таблицы в БД при старте.
    - Закрывает соединения при завершении.
    """
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    yield

    await session.close()
    await engine.dispose()


app = FastAPI(
    title="Кулинарная книга API",
    description="API для управления рецептами с сортировкой по популярности.",
    lifespan=lifespan,
)
app.router.lifespan_context = lifespan


@app.get(
    "/recipes",
    response_model=List[schemas.RecipesOut],
    summary="Список рецептов",
    description="Возвращает все рецепты, "
    "отсортированные по просмотрам и времени приготовления.",
)
async def get_recipes():
    """Получить список рецептов.

    Returns:
        List[RecipesOut]: Список рецептов, отсортированный по:
            - Убыванию просмотров (views DESC).
            - Возрастанию времени приготовления (time_to_cook_in_min ASC).
    """
    res = await session.execute(
        select(models.Recipe).order_by(
            desc(models.Recipe.views), asc(models.Recipe.time_to_cook_in_min)
        )
    )
    return res.scalars().all()


@app.get(
    "/recipes/{recipe_id}",
    response_model=schemas.RecipeInfoOut,
    summary="Детальная информация рецепта",
    description="Возвращает полную информацию о рецепте и "
    "увеличивает счетчик просмотров.",
)
async def get_recipe_info(recipe_id):
    """Получить детали рецепта по ID.

    Args:
        recipe_id (int): Идентификатор рецепта.

    Raises:
        HTTPException: 404, если рецепт не найден.

    Returns:
        RecipeInfoOut: Полная информация о рецепте.
    """
    result = await session.execute(
        select(models.Recipe).where(models.Recipe.id == recipe_id)
    )
    recipe = result.scalars().first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    recipe.views += 1
    return recipe


@app.post(
    "/recipes",
    response_model=schemas.RecipeInfoOut,
    summary="Создать рецепт",
    description="Добавляет новый рецепт в базу данных.",
)
async def create_recipe(recipe: schemas.RecipeIn):
    """Создать новый рецепт.

    Args:
        recipe (RecipeIn): Данные рецепта (название, время,
        ингредиенты, описание).

    Returns:
        RecipeInfoOut: Созданный рецепт (включая присвоенный ID).
    """
    new_recipe = models.Recipe(**recipe.model_dump())
    async with session.begin():
        session.add(new_recipe)
    await session.refresh(new_recipe)
    return new_recipe
