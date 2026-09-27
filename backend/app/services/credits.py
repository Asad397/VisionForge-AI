from app.providers.mock_provider import MockProvider

PROVIDERS = {
    'mock': MockProvider(),
}


def get_provider(provider_name: str):
    provider = PROVIDERS.get(provider_name)
    if provider is None:
        raise ValueError(f'Provider {provider_name} not found')
    return provider


def resolve_provider_for_model(model_name: str, generation_type: str):
    if model_name == 'mock-video' or model_name == 'mock-image':
        return 'mock'
    return 'mock'
