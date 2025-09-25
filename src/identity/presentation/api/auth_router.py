"""
Authentication Router - Clean Architecture Implementation

This router demonstrates the new clean architecture approach:
- Uses use cases instead of directly calling repositories
- Proper separation of concerns
- Domain-driven design principles
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse

from .schemas import (
    LoginRequest, RegisterRequest, AuthResponse, UserResponse, 
    RegisterResponse, VerifyEmailRequest, VerifyEmailResponse, ErrorResponse
)
from src.identity.application.use_cases.register_user import RegisterUserUseCase, RegisterUserCommand
from src.identity.application.use_cases.authenticate_user import AuthenticateUserUseCase, AuthenticateUserCommand
from src.identity.application.use_cases.verify_email import VerifyEmailUseCase, VerifyEmailCommand
from src.identity.infrastructure.repositories.asyncpg_user_repository import AsyncpgUserRepository
from src.identity.infrastructure.external.jwt_token_service import JWTTokenService
from src.shared_kernel.domain.exceptions import (
    DomainException, EntityAlreadyExistsError, EntityNotFoundError, 
    ValidationError, BusinessRuleViolationError
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}}
)


# Dependency injection - These would typically be configured in a DI container
async def get_user_repository() -> AsyncpgUserRepository:
    """Get user repository dependency"""
    # This would be injected by the DI container
    from infra.db.connection import get_pool
    pool = await get_pool()
    return AsyncpgUserRepository(pool)


async def get_jwt_service() -> JWTTokenService:
    """Get JWT service dependency"""
    return JWTTokenService()


async def get_register_use_case(
    user_repo: AsyncpgUserRepository = Depends(get_user_repository)
) -> RegisterUserUseCase:
    """Get register user use case"""
    return RegisterUserUseCase(user_repo)


async def get_authenticate_use_case(
    user_repo: AsyncpgUserRepository = Depends(get_user_repository)
) -> AuthenticateUserUseCase:
    """Get authenticate user use case"""
    return AuthenticateUserUseCase(user_repo)


async def get_verify_email_use_case(
    user_repo: AsyncpgUserRepository = Depends(get_user_repository)
) -> VerifyEmailUseCase:
    """Get verify email use case"""
    return VerifyEmailUseCase(user_repo)


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    use_case: RegisterUserUseCase = Depends(get_register_use_case)
):
    """
    Register a new user account.
    
    This endpoint demonstrates clean architecture principles:
    - Router only handles HTTP concerns (request/response)
    - Business logic is in the use case
    - Domain validations are handled by the domain entities
    """
    try:
        command = RegisterUserCommand(
            email=request.email,
            username=request.username,
            password=request.password,
            full_name=request.full_name
        )
        
        result = await use_case.execute(command)
        
        logger.info(f"User registered successfully: {result.username}")
        
        return RegisterResponse(
            message="Registration successful. Please check your email for verification." if result.requires_verification else "Registration successful.",
            user_id=result.user_id,
            email=result.email,
            requires_verification=result.requires_verification
        )
        
    except EntityAlreadyExistsError as e:
        logger.warning(f"Registration failed - entity exists: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except ValidationError as e:
        logger.warning(f"Registration failed - validation error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Registration failed - unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    http_request: Request,
    use_case: AuthenticateUserUseCase = Depends(get_authenticate_use_case),
    jwt_service: JWTTokenService = Depends(get_jwt_service)
):
    """
    Authenticate user and return JWT tokens.
    
    Clean architecture benefits demonstrated:
    - Clear separation between HTTP handling and business logic
    - Domain events can be easily added to track login attempts
    - Business rules are enforced in the domain layer
    """
    try:
        # Get client IP for security tracking
        client_ip = http_request.client.host if http_request.client else None
        user_agent = http_request.headers.get("User-Agent")
        
        command = AuthenticateUserCommand(
            email=request.email,
            password=request.password,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        result = await use_case.execute(command)
        
        # Generate JWT tokens
        access_token = jwt_service.create_access_token(
            user_id=result.user_id,
            email=result.email,
            role=result.role
        )
        
        refresh_token = jwt_service.create_refresh_token(user_id=result.user_id)
        
        logger.info(f"User authenticated successfully: {result.username}")
        
        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60,  # 30 minutes
            user=UserResponse(
                id=result.user_id,
                email=result.email,
                username=result.username,
                full_name=result.full_name,
                role=result.role,
                status=result.status,
                created_at=datetime.utcnow(),  # This should come from the result
                last_login=datetime.utcnow()
            )
        )
        
    except EntityNotFoundError as e:
        logger.warning(f"Login failed - user not found: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    except BusinessRuleViolationError as e:
        logger.warning(f"Login failed - business rule violation: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Login failed - unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(
    request: VerifyEmailRequest,
    use_case: VerifyEmailUseCase = Depends(get_verify_email_use_case)
):
    """
    Verify user email address using verification token.
    
    This endpoint shows how domain events could be used:
    - Email verification could trigger welcome email
    - Analytics could track verification rates
    - Account activation could trigger other domain events
    """
    try:
        command = VerifyEmailCommand(token=request.token)
        result = await use_case.execute(command)
        
        logger.info(f"Email verified successfully for user: {result.user_id}")
        
        return VerifyEmailResponse(
            message="Email verified successfully. Your account is now active.",
            user_id=result.user_id,
            verified=result.verified
        )
        
    except EntityNotFoundError as e:
        logger.warning(f"Email verification failed - token not found: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    except BusinessRuleViolationError as e:
        logger.warning(f"Email verification failed - business rule: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Email verification failed - unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        )


# Domain exception handling would be registered at the app level
# Example: app.add_exception_handler(DomainException, domain_exception_handler)
