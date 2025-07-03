document.addEventListener('DOMContentLoaded', function () {
    const updateButtons = document.querySelectorAll('.update-quantity');
    let removeButtons = document.querySelectorAll('.btn-outline-danger');

    const itemData = {};
    document.querySelectorAll('.stock').forEach(input => {
        const itemId = input.getAttribute('data-item-id');
        const stock_value = parseInt(input.textContent.split(':')[1]);
        const quantityInput = document.querySelector(`.quantity-input[data-item-id="${itemId}"]`);
        const inputValue = parseInt(quantityInput.value);
        itemData[itemId] = {
            remaining_product: stock_value - inputValue,
        };
    });



    updateButtons.forEach(button => {
        button.addEventListener('click', function () {
            const itemId = this.getAttribute('data-item-id');
            const stock_value = parseInt(button.textContent.split(':')[1])
            const action = this.getAttribute('data-action');
            const quantityInput = document.querySelector(`.quantity-input[data-item-id="${itemId}"]`);
            let remaining_prod = itemData[itemId].remaining_product;
            const quantity = parseInt(quantityInput.value);
            let newQuantity = quantity;

            if (action === 'increase' && newQuantity <= stock_value) {
                newQuantity++;
                itemData[itemId].remaining_product--;
            }
            else if (newQuantity > stock_value){
                alert(`You can only order ${stock_value} items`);
                document.querySelector(`.update-quantity[data-item-id="${itemId}"][data-action="increase"]`).classList.add('disabled');

            }
            else if (action === 'decrease' && newQuantity > 1 ) {
                if (newQuantity === 2) {
                    document.querySelector(`.update-quantity[data-item-id="${itemId}"][data-action="increase"]`).classList.remove('disabled');
                }
                newQuantity--;
                itemData[itemId].remaining_product++;


            }


            // Update the quantity input field
            quantityInput.value = newQuantity;

            if (newQuantity === 1 ) {
                this.classList.add('disabled');
            } else if(quantity === 1 && newQuantity > 1 && action === 'increase') {
                document.querySelector(`.update-quantity[data-item-id="${itemId}"][data-action="decrease"]`).classList.remove('disabled');

            }

            // Send AJAX request to update the quantity on the server
            fetch(`/cart/update/${itemId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ quantity: newQuantity})
            })
                .then(response => response.json())
                .then(data => {// Update the subtotal and total dynamically
                    document.querySelector(`#subtotal-${itemId}`).textContent = `${data.subtotal}€`;
                    document.querySelector('#cart-total').textContent = `${data.total}€`;
                    document.querySelector('#cart-tax').textContent = `${data.tax}€`;
                    document.querySelector('#cart-gran-total').textContent = `${data.grand_total}€`;
                    document.querySelector(`#stock-${itemId}`).textContent = `Remaining: ${itemData[itemId].remaining_product}`;

                })
                .catch(error => console.error('Error:', error));
        });
    });

    removeButtons.forEach(button => {
        button.addEventListener('click', function () {
            const itemId = this.getAttribute('data-item-id');

            // Send AJAX request to remove the item from the server
            fetch(`/cart/remove/${itemId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.empty) {
                        window.location.assign('/cart/');
                        return;
                    }
                    // Remove the item row from the table
                    document.querySelector(`#cart-item-row-${itemId}`).remove();

                    // Update the total dynamically
                    document.querySelector('#cart_icon_number').textContent = `${data.cart_items_count}`;
                    document.querySelector('#cart-total').textContent = `${data.total}€`;
                    document.querySelector('#cart-tax').textContent = `${data.tax}€`;
                    document.querySelector('#cart-gran-total').textContent = `${data.grand_total}€`;
                    document.querySelector(`#stock-${itemId}`).textContent = `Remaining: ${itemData[itemId].remaining_product}`;

                })
                .catch(error => console.error('Error:', error));
        });
    });
});
