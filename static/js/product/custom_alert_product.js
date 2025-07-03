const input = document.getElementById('quantity');
const quantityInput = document.getElementById('quantity');
const maxValue = quantityInput.max;
input.addEventListener('input', () => {
    if (input.validity.rangeOverflow) {
        input.setCustomValidity("we currently have " + maxValue + " products in stock");
    } else {
        input.setCustomValidity("");
    }
});