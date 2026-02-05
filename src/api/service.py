import asyncio
import uuid
import os
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from ..repository.interface import TaggedResource
from ..repository.dict_repository import DictResourceRepository
from ..agents.web_analyzer import WebLinkAnalyzer
from ..agents.text_analyzer import TextAnalyzer
from ..auth.interface import AuthRepository
from ..auth.file_repository import FileAuthRepository
from ..auth.jwt_handler import JWTHandler
from ..auth.middleware import create_auth_dependency


app = FastAPI(title="Tag Notes API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize repository and agents
repository = DictResourceRepository()
web_analyzer = WebLinkAnalyzer()
text_analyzer = TextAnalyzer()

# Initialize authentication
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
auth_repository: AuthRepository = FileAuthRepository()
jwt_handler = JWTHandler(secret_key=SECRET_KEY, expiration_hours=24)
verify_token = create_auth_dependency(jwt_handler)

# Thread pool for running agents concurrently
executor = ThreadPoolExecutor(max_workers=2)


class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str


class AddResourceRequest(BaseModel):
    content: str
    tags: Optional[List[str]] = None
    description: Optional[str] = None


class ResourceResponse(BaseModel):
    id: str
    content: str
    resource_type: str
    tags: List[str]
    description: str


class SearchRequest(BaseModel):
    tag: str


def is_url(text: str) -> bool:
    """Check if text is a URL"""
    return text.startswith(("http://", "https://"))


def analyze_web_link(url: str) -> tuple:
    """Wrapper for web analyzer"""
    return web_analyzer.analyze(url)


def analyze_text(text: str) -> tuple:
    """Wrapper for text analyzer"""
    return text_analyzer.analyze(text)


@app.post("/api/auth/signup", response_model=AuthResponse)
async def signup(request: SignupRequest):
    """Register a new user"""
    if len(request.password) < 6:
        raise HTTPException(
            status_code=400, detail="Password must be at least 6 characters"
        )

    # Hash password
    hashed_password = FileAuthRepository.hash_password(request.password)

    # Create user
    success = auth_repository.create_user(request.email, hashed_password)

    if not success:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate JWT token
    token = jwt_handler.create_token(request.email)

    return AuthResponse(access_token=token, email=request.email)


@app.post("/api/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login a user"""
    # Get user
    user = auth_repository.get_user(request.email)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Verify password
    hashed_password = FileAuthRepository.hash_password(request.password)
    if user.hashed_password != hashed_password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate JWT token
    token = jwt_handler.create_token(request.email)

    return AuthResponse(access_token=token, email=request.email)


@app.post("/api/add", response_model=ResourceResponse)
async def add_resource(
    request: AddResourceRequest, current_user: str = Depends(verify_token)
):
    """Add a new resource (web link or text)"""
    content = request.content.strip()

    if not content:
        raise HTTPException(status_code=400, detail="Content cannot be empty")

    # Determine resource type
    resource_type = "web" if is_url(content) else "text"

    try:
        # Check if custom tags and description provided
        if request.tags and request.description:
            tags = request.tags
            description = request.description
        else:
            # Run analysis in thread pool
            loop = asyncio.get_event_loop()
            if resource_type == "web":
                tags, description = await loop.run_in_executor(
                    executor, analyze_web_link, content
                )
            else:
                tags, description = await loop.run_in_executor(
                    executor, analyze_text, content
                )

        # Create and save resource
        resource = TaggedResource(
            id=str(uuid.uuid4()),
            content=content,
            resource_type=resource_type,
            tags=tags,
            description=description,
            user_email=current_user,
        )

        repository.save(resource)

        return ResourceResponse(
            id=resource.id,
            content=resource.content,
            resource_type=resource.resource_type,
            tags=resource.tags,
            description=resource.description,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing resource: {str(e)}"
        )


@app.post("/api/search", response_model=List[ResourceResponse])
async def search_by_tag(
    request: SearchRequest, current_user: str = Depends(verify_token)
):
    """Search resources by tag"""
    tag = request.tag.strip()

    if not tag:
        raise HTTPException(status_code=400, detail="Tag cannot be empty")

    resources = repository.find_by_tag(tag, current_user)

    return [
        ResourceResponse(
            id=r.id,
            content=r.content,
            resource_type=r.resource_type,
            tags=r.tags,
            description=r.description,
        )
        for r in resources
    ]


@app.get("/api/resources", response_model=List[ResourceResponse])
async def get_all_resources(current_user: str = Depends(verify_token)):
    """Get all resources for the authenticated user"""
    resources = repository.get_all(current_user)

    return [
        ResourceResponse(
            id=r.id,
            content=r.content,
            resource_type=r.resource_type,
            tags=r.tags,
            description=r.description,
        )
        for r in resources
    ]


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
