
document.addEventListener('DOMContentLoaded', () => {
    const itemData = {};
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const qs = (selector) => document.querySelector(selector);
    const qsa = (selector) => document.querySelectorAll(selector);

    const updateUI = (itemId, quantity, stockValue) => {
        const increaseBtn = qs(`.update-quantity[data-item-id="${itemId}"][data-action="increase"]`);
        const decreaseBtn = qs(`.update-quantity[data-item-id="${itemId}"][data-action="decrease"]`);

        increaseBtn.classList.toggle('disabled', quantity >= stockValue);
        decreaseBtn.classList.toggle('disabled', quantity <= 1);
    };

    const updateTotals = (data, itemId) => {
        qs(`#subtotal-${itemId}`).textContent = `${data.subtotal}€`;
        qs('#cart-total').textContent = `${data.total}€`;
        qs('#cart-tax').textContent = `${data.tax}€`;
        qs('#cart-gran-total').textContent = `${data.grand_total}€`;
        qs(`#stock-${itemId}`).textContent = `Remaining: ${itemData[itemId].remaining_product}`;

        const d_subtotal = qs(`#d-subtotal-${itemId}`);
        if (d_subtotal) d_subtotal.textContent = `${data.discounted_subtotal}€`;

        qs('#d-cart-total').textContent = `${data.discounted_total}€`;
        qs('#d-cart-tax').textContent = `${data.discounted_tax}€`;
        qs('#d-cart-gran-total').textContent = `${data.discounted_grand_total}€`;
    };

    qsa('.stock').forEach(el => {
        const itemId = el.dataset.itemId;
        const stockValue = parseInt(el.textContent.split(':')[1]);
        const input = qs(`.quantity-input[data-item-id="${itemId}"]`);
        const value = parseInt(input.value);

        itemData[itemId] = {
            stock_value: stockValue,
            remaining_product: stockValue - value,
        };

        updateUI(itemId, value, stockValue);
    });

    qsa('.update-quantity').forEach(button => {
        button.addEventListener('click', () => {
            const itemId = button.dataset.itemId;
            const action = button.dataset.action;
            const stockValue = itemData[itemId].stock_value;
            const input = qs(`.quantity-input[data-item-id="${itemId}"]`);
            let quantity = parseInt(input.value);

            if (action === 'increase') {
                if (quantity >= stockValue) {
                    alert(`You can only order ${stockValue} items`);
                    return;
                }
                quantity++;
                itemData[itemId].remaining_product--;
            } else if (action === 'decrease' && quantity > 1) {
                quantity--;
                itemData[itemId].remaining_product++;
            }

            input.value = quantity;
            updateUI(itemId, quantity, stockValue);

            showSpinner();

            fetch(`/cart/update/${itemId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ quantity })
            })
                .then(res => res.json())
                .then(data => updateTotals(data, itemId))
                .catch(err => console.error('Error:', err))
                .finally(() => {
                    hideSpinner();

                });
        });
    });

    // Gestione rimozione item
    qsa('.btn-outline-danger').forEach(button => {
        button.addEventListener('click', () => {
            const itemId = button.dataset.itemId;

            // Optional: mostra spinner
            showSpinner();

            fetch(`/cart/remove/${itemId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            })
                .then(res => res.json())
                .then(data => {
                    if (data.empty) {
                        window.location.assign('/cart/');
                        return;
                    }

                    qs(`#cart-item-row-${itemId}`)?.remove();
                    qs('#cart_icon_number').textContent = `${data.cart_items_count}`;
                    updateTotals(data, itemId);
                })
                .catch(err => console.error('Error:', err))
                .finally(() => {
                    hideSpinner()

                });
        });
    });
});
function showSpinner() {
    // 1. Crea il contenitore principale
    const overlay = document.createElement('div');
    overlay.id = 'loading-spinner';
    overlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center  bg-opacity-75';
    overlay.style.zIndex = '1050';

    // 2. Crea l’elemento spinner interno
    const spinner = document.createElement('div');
    spinner.className = 'spinner-border text-primary';
    spinner.setAttribute('role', 'status');
    spinner.style.width = '3rem';
    spinner.style.height = '3rem';

    // 3. Inserisci lo spinner dentro l’overlay
    overlay.appendChild(spinner);

    // 4. Appendi l’overlay al body
    document.body.appendChild(overlay);
}


function hideSpinner() {
    const overlay = document.getElementById('loading-spinner');
    if (overlay) {
        overlay.remove();
    }
}

