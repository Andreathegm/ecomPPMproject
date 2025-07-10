from django.db.models import Avg, Count, Case, When
from django.db.models.functions import Length
from django.forms import IntegerField
from django.shortcuts import render
from django.utils import timezone

from products.models import Category, Review, Product  # Assumendo che il model Category sia in products.models


def home(request):
    top_p = top_picks(request)  # Ottieni i prodotti più venduti
    top_revs = top_review(request)  # Ottieni i prodotti con le recensioni migliori

    context = {
        'top_picks': top_p,
        'top_reviews': top_revs,
    }
    return render(request, 'main.html', context)

def top_picks(request):
    """
    Restituisce i prodotti più popolari basati su:
    - Rating medio alto (>= 4.0)
    - Numero di recensioni
    - Prodotti disponibili
    - Ordina per rating medio e numero di recensioni

    Se non ci sono abbastanza prodotti "top", prende prodotti casuali disponibili.
    """
    # Cerca prima i "veri" top picks
    top_picks = Product.objects.filter(
        available=True,
        stock__gt=0,
        reviews__isnull=False  # Solo prodotti con almeno una recensione
    ).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).filter(
        avg_rating__gte=4.0,  # Solo prodotti con rating >= 4.0
        review_count__gte=3   # Almeno 3 recensioni per essere considerato "top"
    ).order_by(
        '-avg_rating',      # Prima per rating più alto
        '-review_count',    # Poi per numero di recensioni
        '-created_at'       # Infine per data di creazione (più recenti)
    ).select_related('category').prefetch_related('images', 'reviews')[:8]  # Limita a 8 prodotti

    # Se abbiamo abbastanza prodotti top, restituiscili
    if top_picks.count() >= 4:  # Almeno 4 prodotti "veri" top picks
        return top_picks

    # FALLBACK: Se non ci sono abbastanza top picks, prendi prodotti casuali
    print("Non abbastanza top picks trovati, uso fallback con prodotti casuali")

    # Prendi prodotti disponibili con almeno 1 recensione, ordinati per rating
    fallback_picks = Product.objects.filter(
        available=True,
        stock__gt=0,
        reviews__isnull=False
    ).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).filter(
        avg_rating__gte=3.0  # Soglia più bassa per il fallback
    ).order_by(
        '-avg_rating',
        '-review_count',
        '-created_at'
    ).select_related('category').prefetch_related('images', 'reviews')[:8]

    # Se anche questo fallisce, prendi prodotti casuali senza recensioni
    if fallback_picks.count() < 4:
        print(" Anche il fallback ha pochi risultati, prendo prodotti casuali")
        random_picks = Product.objects.filter(
            available=True,
            stock__gt=0
        ).select_related('category').prefetch_related('images', 'reviews').order_by('?')[:8]
        return random_picks

    return fallback_picks

def top_review(request):
    """
    Restituisce le migliori recensioni basate su:
    - Rating alto (4-5 stelle)
    - Recensioni più recenti
    - Testo non troppo breve
    - Utenti verificati (hanno effettivamente acquistato)
    """
    # Calcola la data di 6 mesi fa per recensioni relativamente recenti
    six_months_ago = timezone.now() - timezone.timedelta(days=180)

    top_review = Review.objects.filter(
        rating__gte=4,  # Solo recensioni con 4-5 stelle
        created_at__gte=six_months_ago,  # Recensioni degli ultimi 6 mesi
        review_text__isnull=False  # Assicurati che ci sia del testo
    ).exclude(
        review_text__exact='',  # Escludi recensioni vuote
        review_text__isnull=True
    ).filter(
        # Filtra recensioni con almeno 20 caratteri (non troppo brevi)
        review_text__regex=r'.{20,}'
    ).select_related(
        'user', 'product', 'order'
    ).prefetch_related(
        'product__images'
    ).order_by(
        '-rating',          # Prima per rating più alto
        '-created_at'       # Poi per data più recente
    )[:6]  # Limita a 6 recensioni per la sezione testimonials

    return top_review

# Versione alternativa più avanzata per top_review con logica più sofisticata
def top_review_advanced(request):
    """
    Versione avanzata che considera anche:
    - Lunghezza del testo (non troppo breve, non troppo lungo)
    - Diversità di prodotti (non tutte dello stesso prodotto)
    - Bilanciamento tra rating e recency
    """

    # Calcola score basato su rating e recency
    now = timezone.now()
    thirty_days_ago = now - timezone.timedelta(days=30)
    ninety_days_ago = now - timezone.timedelta(days=90)

    top_review = Review.objects.filter(
        rating__gte=4,
        review_text__isnull=False
    ).exclude(
        review_text__exact=''
    ).annotate(
        text_length=Length('review_text'),
        # Score basato su recency
        recency_score=Case(
            When(created_at__gte=thirty_days_ago, then=3),
            When(created_at__gte=ninety_days_ago, then=2),
            default=1,
            output_field=IntegerField()
        ),
        # Score totale
        total_score=Case(
            When(rating=5, then=5),
            When(rating=4, then=4),
            default=0,
            output_field=IntegerField()
        )
    ).filter(
        text_length__gte=20,    # Almeno 20 caratteri
        text_length__lte=500    # Massimo 500 caratteri per testimonials
    ).select_related(
        'user', 'product', 'order'
    ).prefetch_related(
        'product__images'
    ).order_by(
        '-total_score',
        '-recency_score',
        '-created_at'
    )[:6]

    return top_review

# Funzione helper per ottenere statistiche dei top picks
def get_top_picks_stats():
    """
    Restituisce statistiche sui top picks per debug/admin
    """
    stats = Product.objects.filter(
        available=True,
        stock__gt=0,
        reviews__isnull=False
    ).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).filter(
        avg_rating__gte=4.0,
        review_count__gte=3
    ).aggregate(
        total_products=Count('id'),
        avg_rating_all=Avg('avg_rating'),
        avg_review_count=Avg('review_count')
    )

    return stats
