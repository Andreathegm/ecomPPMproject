// function handlePriceInput(slider) {
//     const span = document.getElementById('priceValue');
//
//     span.textContent = slider.value;
//
//     if (!slider.hasAttribute('name')) {
//         slider.setAttribute('name', 'max_price');
//     }
// }
//
// document.addEventListener('DOMContentLoaded', () => {
//     const clearBtn     = document.getElementById('clearFilters');
//     const categorySel  = document.getElementById('categoryDropdown');
//     const orderSel     = document.querySelector('select[name="order"]');
//     const priceRange   = document.getElementById('priceRange');
//     const salecheckbox = document.getElementById('onsaleCheckbox');
//     id="onsaleCheckbox"
//
//
//
//
//
//     function onPriceInput() {
//         handlePriceInput(priceRange);
//         updateClearBtn();
//     }
//
//     function updateClearBtn() {
//         const priceActive = priceRange.hasAttribute('name');
//         const catActive   = categorySel.value !== '';
//         const orderActive = orderSel.value    !== '';
//         const saleActive  = salecheckbox.checked;
//
//         if (priceActive || catActive || orderActive || saleActive) {
//             clearBtn.classList.remove('d-none');
//         } else {
//             clearBtn.classList.add('d-none');
//         }
//     }
//
//     // listener
//     categorySel.addEventListener('change', updateClearBtn);
//     orderSel.addEventListener('change', updateClearBtn);
//     priceRange.addEventListener('input', onPriceInput);
//     salecheckbox.addEventListener('change', updateClearBtn);
//
//     updateClearBtn();
// });
// // Star rating filter functionality
// document.addEventListener('DOMContentLoaded', function() {
//     const ratingFilter = document.getElementById('ratingFilter');
//     const minRatingInput = document.getElementById('minRatingInput');
//     const stars = ratingFilter.querySelectorAll('.star');
//
//     // Initialize stars based on current rating
//     const currentRating = parseInt(ratingFilter.dataset.rating) || 0;
//     updateStarDisplay(currentRating);
//
//     // Add click event listeners to stars
//     stars.forEach(star => {
//         star.addEventListener('click', function() {
//             const rating = parseInt(this.dataset.value);
//
//             // If clicking the same star that's already selected, clear the filter
//             if (rating === currentRating) {
//                 minRatingInput.value = '';
//                 ratingFilter.dataset.rating = '0';
//                 updateStarDisplay(0);
//             } else {
//                 minRatingInput.value = rating;
//                 ratingFilter.dataset.rating = rating;
//                 updateStarDisplay(rating);
//             }
//         });
//
//         // Add hover effects
//         star.addEventListener('mouseenter', function() {
//             const hoverRating = parseInt(this.dataset.value);
//             updateStarDisplay(hoverRating, true);
//         });
//     });
//
//     // Reset to selected rating when mouse leaves
//     ratingFilter.addEventListener('mouseleave', function() {
//         const selectedRating = parseInt(ratingFilter.dataset.rating) || 0;
//         updateStarDisplay(selectedRating);
//     });
//
//     function updateStarDisplay(rating, isHover = false) {
//         stars.forEach((star, index) => {
//             const starIcon = star.querySelector('i');
//             const starValue = index + 1;
//
//             if (starValue <= rating) {
//                 starIcon.className = 'fa-solid fa-star';
//                 starIcon.style.color = isHover ? '#ffc107' : '#f39c12';
//             } else {
//                 starIcon.className = 'fa-regular fa-star';
//                 starIcon.style.color = '#6c757d';
//             }
//         });
//     }
// });
function handlePriceInput(slider) {
    const span = document.getElementById('priceValue');

    span.textContent = slider.value;

    if (!slider.hasAttribute('name')) {
        slider.setAttribute('name', 'max_price');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const clearBtn     = document.getElementById('clearFilters');
    const categorySel  = document.getElementById('categoryDropdown');
    const orderSel     = document.querySelector('select[name="order"]');
    const priceRange   = document.getElementById('priceRange');
    const salecheckbox = document.getElementById('onsaleCheckbox');

    // Rating elements
    const ratingFilter = document.getElementById('ratingFilter');
    const minRatingInput = document.getElementById('minRatingInput');
    const stars = ratingFilter ? ratingFilter.querySelectorAll('.star') : [];

    function onPriceInput() {
        handlePriceInput(priceRange);
        updateClearBtn();
    }

    function updateClearBtn() {
        const priceActive = priceRange.hasAttribute('name');
        const catActive   = categorySel.value !== '';
        const orderActive = orderSel.value !== '';
        const saleActive  = salecheckbox.checked;
        const ratingActive = minRatingInput && minRatingInput.value !== '';

        if (priceActive || catActive || orderActive || saleActive || ratingActive) {
            clearBtn.classList.remove('d-none');
        } else {
            clearBtn.classList.add('d-none');
        }
    }

    // Star rating filter functionality
    if (ratingFilter && minRatingInput) {
        // Initialize stars based on current rating
        const currentRating = parseInt(ratingFilter.dataset.rating) || 0;
        updateStarDisplay(currentRating);

        // Add click event listeners to stars
        stars.forEach(star => {
            star.addEventListener('click', function() {
                const rating = parseInt(this.dataset.value);
                const previousRating = parseInt(ratingFilter.dataset.rating) || 0;

                // If clicking the same star that's already selected, clear the filter
                if (rating === previousRating) {
                    minRatingInput.value = '';
                    ratingFilter.dataset.rating = '0';
                    updateStarDisplay(0);
                } else {
                    minRatingInput.value = rating;
                    ratingFilter.dataset.rating = rating;
                    updateStarDisplay(rating);
                }

                // Update clear button visibility after rating change
                updateClearBtn();
            });

            // Add hover effects
            star.addEventListener('mouseenter', function() {
                const hoverRating = parseInt(this.dataset.value);
                updateStarDisplay(hoverRating, true);
            });
        });

        // Reset to selected rating when mouse leaves
        ratingFilter.addEventListener('mouseleave', function() {
            const selectedRating = parseInt(ratingFilter.dataset.rating) || 0;
            updateStarDisplay(selectedRating);
        });

        function updateStarDisplay(rating, isHover = false) {
            stars.forEach((star, index) => {
                const starIcon = star.querySelector('i');
                const starValue = index + 1;

                if (starValue <= rating) {
                    starIcon.className = 'fa-solid fa-star';
                    starIcon.style.color = isHover ? '#ffc107' : '#f39c12';
                } else {
                    starIcon.className = 'fa-regular fa-star';
                    starIcon.style.color = '#6c757d';
                }
            });
        }
    }

    // Event listeners
    categorySel.addEventListener('change', updateClearBtn);
    orderSel.addEventListener('change', updateClearBtn);
    priceRange.addEventListener('input', onPriceInput);
    salecheckbox.addEventListener('change', updateClearBtn);

    // Initial update
    updateClearBtn();
});