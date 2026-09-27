from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import Base, engine, get_db
from app.models import User, ModelRecord, Generation, CreditTransaction, Character, FileRecord, JobRecord
from app.security import get_current_user, get_admin_user, get_password_hash, verify_password, create_access_token
from app.schemas import UserCreate, UserLogin, UserResponse, TokenResponse, GenerationCreate, ModelSchema, GenerationResponse, CharacterCreate, FileUploadResponse, CreditTransactionResponse
from app.services.credits import CreditService
from app.providers.registry import resolve_provider_for_model
from app.tasks import process_generation
from app.models import GenerationOutput
from app.tasks import celery_app

settings = get_settings()
app = FastAPI(title='VisionForge AI API', version='0.1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

Base.metadata.create_all(bind=engine)


@app.get('/')
def root():
    return {'app': 'VisionForge AI', 'status': 'ok'}


@app.post('/api/auth/register', response_model=TokenResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail='Email already registered')

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        credits=100,
        is_active=True,
    )
    db.add(user)
    db.commit(); db.refresh(user)

    token = create_access_token({'sub': user.email})
    return {'access_token': token, 'token_type': 'bearer'}


@app.post('/api/auth/login', response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Invalid credentials')

    token = create_access_token({'sub': user.email})
    return {'access_token': token, 'token_type': 'bearer'}


@app.get('/api/auth/me', response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get('/api/models', response_model=list[ModelSchema])
def list_models(db: Session = Depends(get_db)):
    records = db.query(ModelRecord).filter(ModelRecord.enabled == True).all()
    return records


@app.post('/api/generations', response_model=GenerationResponse)
def create_generation(payload: GenerationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    model = db.query(ModelRecord).filter(ModelRecord.id == payload.model_id).first()
    if not model or not model.enabled:
        raise HTTPException(status_code=404, detail='Model not available')

    if current_user.credits < model.credit_cost:
        raise HTTPException(status_code=402, detail='Insufficient credits')

    current_user.credits -= model.credit_cost
    db.add(CreditTransaction(user_id=current_user.id, generation_id=None, amount=-model.credit_cost, reason='generation_reserved', balance_after=current_user.credits))
    db.commit(); db.refresh(current_user)

    generation = Generation(
        user_id=current_user.id,
        model_id=model.id,
        generation_type=payload.generation_type,
        prompt=payload.prompt,
        negative_prompt=payload.negative_prompt,
        provider=model.provider,
        model_name=model.name,
        resolution=payload.resolution or (model.supported_resolutions[0] if model.supported_resolutions else '1024x1024'),
        aspect_ratio=payload.aspect_ratio,
        duration=payload.duration,
        status='queued',
        progress=0,
    )
    db.add(generation)
    db.commit(); db.refresh(generation)

    db.add(JobRecord(generation_id=generation.id, provider=model.provider, model=model.name, status='queued', attempts=0, progress=0))
    db.commit()

    if settings.ai_mock_mode:
        process_generation.delay(generation.id)
    else:
        if model.provider == 'mock':
            process_generation.delay(generation.id)

    return generation


@app.get('/api/generations', response_model=list[GenerationResponse])
def list_generations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Generation).filter(Generation.user_id == current_user.id).order_by(Generation.created_at.desc()).all()


@app.get('/api/generations/{generation_id}', response_model=GenerationResponse)
def get_generation(generation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    generation = db.query(Generation).filter(Generation.id == generation_id, Generation.user_id == current_user.id).first()
    if not generation:
        raise HTTPException(status_code=404, detail='Generation not found')
    return generation


@app.post('/api/credits')
def get_credits(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {'credits': current_user.credits}


@app.get('/api/credits/transactions', response_model=list[CreditTransactionResponse])
def credit_transactions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(CreditTransaction).filter(CreditTransaction.user_id == current_user.id).order_by(CreditTransaction.created_at.desc()).all()


@app.post('/api/characters', response_model=dict)
def create_character(payload: CharacterCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    character = Character(
        user_id=current_user.id,
        name=payload.name,
        description=payload.description,
        visual_description=payload.visual_description,
        style=payload.style,
        metadata=payload.metadata,
    )
    db.add(character)
    db.commit(); db.refresh(character)
    return {'id': character.id, 'name': character.name}


@app.get('/api/characters', response_model=list)
def list_characters(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Character).filter(Character.user_id == current_user.id).all()


@app.get('/api/admin/users')
def admin_users(db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    return db.query(User).all()


@app.get('/api/admin/jobs')
def admin_jobs(db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    return db.query(JobRecord).all()


@app.get('/api/admin/generations')
def admin_generations(db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    return db.query(Generation).all()


@app.patch('/api/admin/models/{model_id}')
def patch_model(model_id: int, payload: dict, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    model = db.query(ModelRecord).filter(ModelRecord.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail='Model not found')
    for key, value in payload.items():
        setattr(model, key, value)
    db.commit()
    return {'status': 'updated'}


@app.post('/api/files/upload', response_model=FileUploadResponse)
def upload_file(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = FileRecord(
        user_id=current_user.id,
        filename='uploaded-file.bin',
        file_type='application/octet-stream',
        object_key='uploads/uploaded-file.bin',
        size=0,
    )
    db.add(record)
    db.commit(); db.refresh(record)
    return record


@app.get('/api/health')
def health():
    return {'status': 'ok', 'mock_mode': settings.ai_mock_mode}


@app.get('/api/admin/models')
def admin_models(db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    return db.query(ModelRecord).all()


@app.post('/api/admin/seed-models')
def seed_models(db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    defaults = [
        {
            'name': 'Mock Video',
            'provider': 'mock',
            'type': 'TEXT_TO_VIDEO',
            'description': 'Development mock model',
            'enabled': True,
            'credit_cost': 25,
            'capabilities': ['TEXT_TO_VIDEO', 'IMAGE_TO_VIDEO', 'VIDEO_TO_VIDEO'],
            'max_duration': 30,
            'supported_resolutions': ['1280x720', '1024x1024'],
            'supported_ratios': ['16:9', '1:1'],
            'settings_schema': {'duration': {'min': 3, 'max': 30}},
        },
        {
            'name': 'Mock Image',
            'provider': 'mock',
            'type': 'TEXT_TO_IMAGE',
            'description': 'Development mock image model',
            'enabled': True,
            'credit_cost': 10,
            'capabilities': ['TEXT_TO_IMAGE', 'IMAGE_TO_IMAGE'],
            'max_duration': 10,
            'supported_resolutions': ['1024x1024', '1536x1024'],
            'supported_ratios': ['1:1', '3:2'],
            'settings_schema': {'guidance': {'min': 1, 'max': 20}},
        },
    ]

    for item in defaults:
        existing = db.query(ModelRecord).filter(ModelRecord.name == item['name']).first()
        if not existing:
            db.add(ModelRecord(**item))
    db.commit()
    return {'status': 'seeded'}


@app.on_event('startup')
def startup_seed_admin_and_models():
    db: Session = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == settings.admin_email).first()
        if not admin:
            db.add(User(
                email=settings.admin_email,
                hashed_password=get_password_hash(settings.admin_password),
                full_name='Admin',
                is_admin=True,
                credits=5000,
                email_verified=True,
            ))
            db.commit()

        if db.query(ModelRecord).count() == 0:
            db.add_all([
                ModelRecord(
                    name='Mock Video',
                    provider='mock',
                    type='TEXT_TO_VIDEO',
                    description='Development mock model',
                    enabled=True,
                    credit_cost=25,
                    capabilities=['TEXT_TO_VIDEO', 'IMAGE_TO_VIDEO', 'VIDEO_TO_VIDEO'],
                    max_duration=30,
                    supported_resolutions=['1280x720', '1024x1024'],
                    supported_ratios=['16:9', '1:1'],
                    settings_schema={'duration': {'min': 3, 'max': 30}},
                ),
                ModelRecord(
                    name='Mock Image',
                    provider='mock',
                    type='TEXT_TO_IMAGE',
                    description='Development mock image model',
                    enabled=True,
                    credit_cost=10,
                    capabilities=['TEXT_TO_IMAGE', 'IMAGE_TO_IMAGE'],
                    max_duration=10,
                    supported_resolutions=['1024x1024', '1536x1024'],
                    supported_ratios=['1:1', '3:2'],
                    settings_schema={'guidance': {'min': 1, 'max': 20}},
                ),
            ])
            db.commit()
    finally:
        db.close()
