def currency_context(request):
    """Provides user currency symbol to all templates."""
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        return {'currency_symbol': request.user.profile.currency or '₹'}
    return {'currency_symbol': '₹'}
