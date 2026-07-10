from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import PostCreate, PostResponse
from typing import Optional
from database import get_db
from sqlalchemy import text
from auth import get_current_user
from cache import get_cache , set_cache, delete_cache

router = APIRouter(prefix="/posts")


@router.get("/", response_model=list[PostResponse])
async def get_all_post(published: Optional[bool] = None, limit: int = 10, skip: int = 0, db:AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    red_key = f"posts:{published}:{limit}:{skip}"
    cached = await get_cache(red_key)
    if cached:
        print("Cached return")
        return cached

    result = await db.execute(text("SELECT * FROM posts")) #returns tuple
    posts = result.mappings().all()  # returns list of dict-like objects

    if published is not None:
        posts = [p for p in posts if p["published"] == published]

    post_list = [dict(p) for p in posts][skip: skip + limit]
    await set_cache(red_key , post_list)
    print("cache miss - fetched from db")
    return post_list

@router.post("/", response_model=PostResponse , status_code=201)
async def create_post(post: PostCreate, db:AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(
        text("INSERT INTO posts (title, published, content) VALUES (:title, :published, :content) RETURNING id"),
        {"title": post.title, "content": post.content, "published": post.published}
    )
    await db.commit()
    new_id = result.scalar()
    result = await db.execute(text("SELECT * FROM posts WHERE id = :id"), {"id": new_id})
    new_post = result.mappings().first()
    await delete_cache(f"posts:None:10:0")
    return new_post

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db:AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM posts WHERE id = :id"), {"id": post_id})
    post = result.mappings().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.delete("/{post_id}", status_code=204)
async def delete_post(post_id: int, db:AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(text("DELETE FROM posts WHERE id=:id",) , {"id": post_id})
    if result.rowcount == 0:      # rowcount = how many rows affected
        raise HTTPException(status_code=404, detail="Post not found")
    await db.commit()
    await delete_cache(f"posts:None:10:0")


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post: PostCreate, db:AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(text("UPDATE posts SET title=:title, content=:content, published=:published WHERE id=:id") , {"title": post.title, "content": post.content, "published": post.published, "id": post_id})
    await db.commit()

    result = await db.execute(text("SELECT * FROM posts WHERE id = :id"), {"id": post_id})
    new_post = result.mappings().first()
    if not new_post:
         raise HTTPException(status_code=404, detail="Post not found")
    await delete_cache(f"posts:None:10:0")

    return new_post












# PYTHON

# Data types, OOP, decorators, generators
# async/await, threading vs multiprocessing
# Exception handling
# Type hints
# List/dict comprehensions

# FASTAPI

# Routing, path/query params, request body
# Pydantic models + validators
# Dependency injection — Depends()
# Async routes
# Middleware
# Error handling — HTTPException, custom handlers
# Background tasks
# WebSockets

# DATABASE

# SQL — joins, indexes, transactions
# SQLAlchemy ORM
# Alembic migrations
# PostgreSQL (not SQLite — they'll ask this)
# Redis basics

# AUTH & SECURITY

# JWT — access + refresh tokens
# OAuth2
# Password hashing
# CORS
# Rate limiting
# SQL injection prevention

# REACT (you're strong here)

# Hooks — useEffect, useState, useMemo, useCallback
# Performance — memo, lazy loading, code splitting
# State management — Redux, Context
# TypeScript basics
# Testing — Jest, React Testing Library

# AWS

# EC2, S3, RDS, Lambda basics
# API Gateway
# IAM roles

# DEVOPS

# Docker + docker-compose
# GitHub Actions CI/CD
# Basic Kubernetes concepts

# SYSTEM DESIGN

# REST API design principles
# Microservices basics
# Caching strategies
# Database design
