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
    const salecheckbox = document.getElementById('onsaleCheckbox');                                                id="onsaleCheckbox"


    function onPriceInput() {
        handlePriceInput(priceRange);
        updateClearBtn();
    }

    function updateClearBtn() {
        const priceActive = priceRange.hasAttribute('name');
        const catActive   = categorySel.value !== '';
        const orderActive = orderSel.value    !== '';
        const saleActive  = salecheckbox.checked;

        if (priceActive || catActive || orderActive || saleActive) {
            clearBtn.classList.remove('d-none');
        } else {
            clearBtn.classList.add('d-none');
        }
    }

    // listener
    categorySel.addEventListener('change', updateClearBtn);
    orderSel.addEventListener('change', updateClearBtn);
    priceRange.addEventListener('input', onPriceInput);
    salecheckbox.addEventListener('change', updateClearBtn);

    updateClearBtn();
});
