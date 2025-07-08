function handlePriceInput(slider) {
    const span = document.getElementById('priceValue');

    // Aggiorna la label con il valore corrente
    span.textContent = slider.value;

    // Alla prima modifica, assegna il name per includerlo nel GET
    if (!slider.hasAttribute('name')) {
        slider.setAttribute('name', 'max_price');
    }
}

// Facoltativo: reset del name se si vuole ripristinare "Any" via JS
// document.getElementById('filterForm').addEventListener('reset', () => {
//     const slider = document.getElementById('priceRange');
//     slider.removeAttribute('name');
//     document.getElementById('priceValue').textContent = 'Any';
// });

document.addEventListener('DOMContentLoaded', () => {
    const clearBtn     = document.getElementById('clearFilters');
    const categorySel  = document.getElementById('categoryDropdown');
    const orderSel     = document.querySelector('select[name="order"]');
    const priceRange   = document.getElementById('priceRange');
    const salecheckbox = document.getElementById('onsaleCheckbox');                                                id="onsaleCheckbox"


    // Se usi già handlePriceInput per aggiornare la label, lo richiameremo qui
    function onPriceInput() {
        handlePriceInput(priceRange);
        updateClearBtn();
    }

    function updateClearBtn() {
        // considera attivo il filtro prezzo solo se gli hai dato il name (prima modifica)
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

    // init (mostra il pulsante se già ci sono filtri al primo caricamento)
    updateClearBtn();
});
