document.addEventListener('DOMContentLoaded', function() {
    // Inizializza le stelle interattive
    initStars();
});

function initStars() {
    const starContainers = document.querySelectorAll('.review-stars');

    starContainers.forEach(container => {
        const stars = container.querySelectorAll('.star');
        const productId = container.getAttribute('data-product-id');

        stars.forEach((star, index) => {
            // Hover effects
            star.addEventListener('mouseenter', function() {
                highlightStars(stars, index + 1);
            });

            star.addEventListener('mouseleave', function() {
                const currentRating = parseInt(container.getAttribute('data-rating')) || 0;
                highlightStars(stars, currentRating);
            });

            // Click to select rating
            star.addEventListener('click', function() {
                const rating = index + 1;
                container.setAttribute('data-rating', rating);
                document.getElementById(`rating-${productId}`).value = rating;
                highlightStars(stars, rating);
            });
        });
    });
}

function highlightStars(stars, rating) {
    stars.forEach((star, index) => {
        const icon = star.querySelector('i');
        if (index < rating) {
            icon.className = 'fa-solid fa-star text-warning';
        } else {
            icon.className = 'fa-regular fa-star text-muted';
        }
    });
}

function toggleReviewForm(productId, isEdit, rating = 0, reviewText = '') {
    const reviewDisplay = document.getElementById(`review-display-${productId}`);
    const reviewForm = document.getElementById(`review-form-${productId}`);
    const starContainer = reviewForm.querySelector('.review-stars');
    const textarea = document.getElementById(`review-text-${productId}`);

    if (reviewForm.style.display === 'none') {
        // Mostra il form
        reviewForm.style.display = 'block';
        if (reviewDisplay) {
            reviewDisplay.style.display = 'none';
        }

        if (isEdit) {
            starContainer.setAttribute('data-rating', rating);
            document.getElementById(`rating-${productId}`).value = rating;
            textarea.value = reviewText;

            // Aggiorna le stelle visivamente
            const stars = starContainer.querySelectorAll('.star');
            highlightStars(stars, rating);
        }

        // Focus sulla textarea
        textarea.focus();
    } else {
        // Nascondi il form
        reviewForm.style.display = 'none';
        if (reviewDisplay) {
            reviewDisplay.style.display = 'block';
        }

        // Reset del form se non è modifica
        if (!isEdit) {
            starContainer.setAttribute('data-rating', '0');
            document.getElementById(`rating-${productId}`).value = '0';
            textarea.value = '';

            const stars = starContainer.querySelectorAll('.star');
            highlightStars(stars, 0);
        }
    }
}

document.addEventListener('submit', function(e) {
    if (e.target.closest('.review-form')) {
        const form = e.target;
        const rating = parseInt(form.querySelector('input[name="rating"]').value);
        const reviewText = form.querySelector('textarea[name="review_text"]').value.trim();

        if (rating === 0) {
            e.preventDefault();
            alert('Please select a rating before submitting.');
            return false;
        }

        if (reviewText.length < 10) {
            e.preventDefault();
            alert('Review text must be at least 10 characters long.');
            return false;
        }
    }
});