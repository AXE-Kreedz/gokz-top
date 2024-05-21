from fastapi import APIRouter

from app.core.skill_points.formula import get_formula

router = APIRouter()


@router.get("/formulas")
async def get_formulas():
    formula = get_formula()
    return {
        'params': formula['formula'],
        'root': formula['root'],
        'weights': formula['weights'],
        'coefficient': formula['coefficient']
    }
