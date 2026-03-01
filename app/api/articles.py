from typing import Optional, List

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.permissions import can_delete_article, can_update_article
from app.db.deps import get_db
from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleRead, ArticleReplace, ArticleUpdate

router = APIRouter(
    prefix="/articles",
    tags=["Articles"],
)


@router.post(
    "/",
    response_model=ArticleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create article",
    description="Create a new article owned by the authenticated user.",
)
def create_article(
    payload: ArticleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    article = Article(
        title=payload.title,
        content=payload.content,
        owner_id=current_user.id,
    )

    db.add(article)
    db.commit()
    db.refresh(article)

    return article


@router.get(
    "/",
    response_model=List[ArticleRead],
    summary="List articles",
    description="Returns paginated list of articles with optional text search.",
)
def list_articles(
    search: Optional[str] = Query(
        default=None,
        description="Search text in article title or content",
        examples={
            "search_example": {
                "summary": "Search articles",
                "value": "FastAPI",
            }
        },
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of articles returned",
        examples={
            "default_limit": {
                "summary": "Default limit",
                "value": 10,
            }
        },
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of articles to skip",
        examples={
            "start": {
                "summary": "Start from first record",
                "value": 0,
            }
        },
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Article).order_by(Article.id)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (Article.title.ilike(pattern)) | (Article.content.ilike(pattern))
        )

    return query.offset(offset).limit(limit).all()


@router.get(
    "/{article_id}",
    response_model=ArticleRead,
    summary="Get article by id",
    description="Returns a single article by its identifier.",
)
def get_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return article


@router.put(
    "/{article_id}",
    response_model=ArticleRead,
    summary="Replace article",
    description="Fully replaces article content (PUT semantics).",
)
def update_article(
    article_id: int,
    payload: ArticleReplace,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if not can_update_article(current_user, article):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    article.title = payload.title
    article.content = payload.content

    db.commit()
    db.refresh(article)

    return article


@router.patch(
    "/{article_id}",
    response_model=ArticleRead,
    summary="Partially update article",
    description="Updates only provided article fields (PATCH semantics).",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "examples": {
                        "update_title": {
                            "summary": "Update only title",
                            "value": {"title": "New title"},
                        },
                        "update_content": {
                            "summary": "Update only content",
                            "value": {"content": "Updated content"},
                        },
                        "update_both": {
                            "summary": "Update title and content",
                            "value": {"title": "New title", "content": "Updated content"},
                        },
                    }
                }
            },
        }
    },
)
def patch_article(
    article_id: int,
    payload: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if not can_update_article(current_user, article):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    if payload.title is not None:
        article.title = payload.title
    if payload.content is not None:
        article.content = payload.content

    db.commit()
    db.refresh(article)
    return article

@router.delete(
    "/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete article",
    description="Deletes article if user has permission.",
)
def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if not can_delete_article(current_user, article):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    db.delete(article)
    db.commit()

    return None