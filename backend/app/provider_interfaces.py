from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    credits = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    generations = relationship('Generation', back_populates='user')
    credit_transactions = relationship('CreditTransaction', back_populates='user')
    characters = relationship('Character', back_populates='user')


class ModelRecord(Base):
    __tablename__ = 'models'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    provider = Column(String(100), nullable=False)
    type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    enabled = Column(Boolean, default=True)
    credit_cost = Column(Integer, default=10)
    capabilities = Column(JSON, default=list)
    max_duration = Column(Integer, default=10)
    supported_resolutions = Column(JSON, default=list)
    supported_ratios = Column(JSON, default=list)
    settings_schema = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    generations = relationship('Generation', back_populates='model')


class Generation(Base):
    __tablename__ = 'generations'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    model_id = Column(Integer, ForeignKey('models.id'), nullable=False)
    generation_type = Column(String(100), nullable=False)
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    status = Column(String(50), default='queued', index=True)
    provider = Column(String(100), nullable=False)
    model_name = Column(String(255), nullable=False)
    resolution = Column(String(50), nullable=True)
    aspect_ratio = Column(String(20), nullable=True)
    duration = Column(Integer, default=5)
    progress = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    output_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='generations')
    model = relationship('ModelRecord', back_populates='generations')
    outputs = relationship('GenerationOutput', back_populates='generation')
    credit_transactions = relationship('CreditTransaction', back_populates='generation')


class GenerationOutput(Base):
    __tablename__ = 'generation_outputs'

    id = Column(Integer, primary_key=True, index=True)
    generation_id = Column(Integer, ForeignKey('generations.id'), nullable=False, index=True)
    kind = Column(String(50), default='video')
    url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    generation = relationship('Generation', back_populates='outputs')


class CreditTransaction(Base):
    __tablename__ = 'credit_transactions'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    generation_id = Column(Integer, ForeignKey('generations.id'), nullable=True, index=True)
    amount = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=False)
    balance_after = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship('User', back_populates='credit_transactions')
    generation = relationship('Generation', back_populates='credit_transactions')


class Character(Base):
    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    visual_description = Column(Text, nullable=True)
    style = Column(String(200), nullable=True)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='characters')
    references = relationship('CharacterReference', back_populates='character')


class CharacterReference(Base):
    __tablename__ = 'character_references'

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False, index=True)
    file_url = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    character = relationship('Character', back_populates='references')


class FileRecord(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=False)
    object_key = Column(String(255), nullable=False)
    size = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class ProviderRecord(Base):
    __tablename__ = 'providers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    provider_type = Column(String(100), nullable=False)
    enabled = Column(Boolean, default=True)
    config = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class JobRecord(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, index=True)
    generation_id = Column(Integer, ForeignKey('generations.id'), nullable=False, index=True)
    provider = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    status = Column(String(50), default='queued', index=True)
    attempts = Column(Integer, default=0)
    progress = Column(Integer, default=0)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Favorite(Base):
    __tablename__ = 'favorites'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    generation_id = Column(Integer, ForeignKey('generations.id'), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ExplorePost(Base):
    __tablename__ = 'explore_posts'

    id = Column(Integer, primary_key=True, index=True)
    generation_id = Column(Integer, ForeignKey('generations.id'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    privacy = Column(String(20), default='PRIVATE')
    likes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    target_type = Column(String(50), nullable=False)
    target_id = Column(Integer, nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
