    document.addEventListener('DOMContentLoaded', function() {
    const MAX_SECONDARY_IMAGES = 9;
    let currentSecondaryCount = 0;
    let activeFormIndices = new Set([0]); // Il form 0 è sempre attivo per l'immagine principale

    // Debug: mostra informazioni sui form
    console.log('Form inizializzato - Total forms:', document.getElementById('id_productimage_set-TOTAL_FORMS')?.value);

    // Inizializza l'immagine principale
    initMainImageUpload();

    function initMainImageUpload() {
    const mainContainer = document.getElementById('main-image-container');
    const firstForm = document.querySelector('.formset-form[data-form-index="0"]');

    if (firstForm) {
    createImageUploadCard(mainContainer, firstForm, true);
}
}

    function createImageUploadCard(container, formElement, isMain = false) {
    const formIndex = formElement.dataset.formIndex;
    const imageInput = formElement.querySelector('input[type="file"]');
    const altInput = formElement.querySelector('input[name*="alt_text"]');
    const isMainInput = formElement.querySelector('input[name*="is_main"]');
    const deleteInput = formElement.querySelector('input[name*="DELETE"]');

    // Debug
    console.log(`Creando card per form ${formIndex}:`, {
    hasImageInput: !!imageInput,
    hasAltInput: !!altInput,
    hasIsMainInput: !!isMainInput
});

    // Imposta is_main per l'immagine principale
    if (isMain && isMainInput) {
    isMainInput.checked = true;
}

    // Assicurati che DELETE sia false
    if (deleteInput) {
    deleteInput.checked = false;
}

    const cardHtml = `
                    <div class="image-upload-card ${isMain ? 'main-image-card' : 'secondary-image-card'}"
                         data-form-index="${formIndex}">
                        <div class="upload-placeholder">
                            <i class="fas fa-cloud-upload-alt"></i>
                            <h5>${isMain ? 'Immagine Principale' : 'Immagine Secondaria'}</h5>
                            <p class="mb-0">Clicca per selezionare un'immagine</p>
                            <small class="text-muted">JPG, PNG, WEBP (max 5MB)</small>
                        </div>
                        <div class="image-preview" style="display: none;">
                            <img src="" alt="Preview" class="preview-img">
                            ${isMain ? '<div class="main-badge">PRINCIPALE</div>' : ''}
                            <div class="image-actions">
                                <button type="button" class="action-btn change" title="Cambia immagine">
                                    <i class="fas fa-edit"></i>
                                </button>
                                ${!isMain ? '<button type="button" class="action-btn delete" title="Rimuovi"><i class="fas fa-trash"></i></button>' : ''}
                            </div>
                        </div>
                        <div class="field-group">
                            <input type="text" class="form-control form-control-sm"
                                   placeholder="Testo alternativo (opzionale)"
                                   data-alt-input="${formIndex}"
                                   value="${altInput ? altInput.value : ''}">
                        </div>
                    </div>
                `;

    container.innerHTML = cardHtml;
    const card = container.querySelector('.image-upload-card');

    // Collega gli eventi
    setupImageUpload(card, imageInput, altInput, isMain, deleteInput);
}

    function setupImageUpload(card, imageInput, altInput, isMain, deleteInput) {
    const formIndex = card.dataset.formIndex;
    const placeholder = card.querySelector('.upload-placeholder');
    const preview = card.querySelector('.image-preview');
    const previewImg = card.querySelector('.preview-img');
    const changeBtn = card.querySelector('.change');
    const deleteBtn = card.querySelector('.delete');
    const altInputField = card.querySelector('input[data-alt-input]');

    // Sincronizza il campo alt_text
    if (altInputField && altInput) {
    // Sincronizzazione bidirezionale
    altInputField.addEventListener('input', function() {
    altInput.value = this.value;
    console.log(`Alt text aggiornato per form ${formIndex}:`, this.value);
});

    // Inizializza il valore se esiste
    if (altInput.value) {
    altInputField.value = altInput.value;
}
}

    // Click sulla card per aprire file dialog
    card.addEventListener('click', function(e) {
    if (!e.target.closest('.image-actions') && !e.target.closest('.field-group')) {
    imageInput.click();
}
});

    // Cambio immagine
    if (changeBtn) {
    changeBtn.addEventListener('click', function(e) {
    e.stopPropagation();
    imageInput.click();
});
}

    // Elimina immagine
    if (deleteBtn) {
    deleteBtn.addEventListener('click', function(e) {
    e.stopPropagation();
    removeSecondaryImage(card, deleteInput);
});
}

    // Gestione cambio file
    imageInput.addEventListener('change', function(e) {
    const file = e.target.files[0];

    if (file) {
    // Validazione file
    if (!file.type.match('image.*')) {
    alert('Seleziona solo file immagine');
    imageInput.value = ''; // Reset input
    return;
}

    if (file.size > 5 * 1024 * 1024) {
    alert('L\'immagine deve essere inferiore a 5MB');
    imageInput.value = ''; // Reset input
    return;
}

    const reader = new FileReader();
    reader.onload = function(e) {
    previewImg.src = e.target.result;
    card.classList.add('has-image');

    // Aggiungi questo form agli attivi
    activeFormIndices.add(parseInt(formIndex));

    console.log(`Immagine caricata per form ${formIndex}`, {
    fileName: file.name,
    fileSize: file.size,
    activeFormIndices: Array.from(activeFormIndices)
});

    // Mostra la sezione immagini secondarie se è la prima immagine
    if (isMain) {
    showSecondaryImagesSection();
}
};
    reader.readAsDataURL(file);
} else {
    // Se non c'è file, rimuovi dalla preview
    previewImg.src = '';
    card.classList.remove('has-image');
    if (!isMain) {
    activeFormIndices.delete(parseInt(formIndex));
}
}
});
}

    function showSecondaryImagesSection() {
    const section = document.getElementById('secondary-images-section');
    section.style.display = 'block';
    section.classList.add('fade-in');
}

    // Aggiungi immagine secondaria
    document.getElementById('add-image-btn').addEventListener('click', function() {
    if (currentSecondaryCount < MAX_SECONDARY_IMAGES) {
    addSecondaryImage();
}
});

    function addSecondaryImage() {
    const container = document.getElementById('secondary-images-container');
    const availableForms = document.querySelectorAll('.formset-form');

    // Trova il prossimo form disponibile (salta il primo che è per l'immagine principale)
    let nextForm = null;
    for (let i = 1; i < availableForms.length; i++) {
    const form = availableForms[i];
    const formIndex = parseInt(form.dataset.formIndex);
    if (!activeFormIndices.has(formIndex)) {
    nextForm = form;
    break;
}
}

    if (nextForm) {
    const formIndex = parseInt(nextForm.dataset.formIndex);
    activeFormIndices.add(formIndex);

    const colDiv = document.createElement('div');
    colDiv.className = 'col-md-4 fade-in';
    colDiv.dataset.formIndex = formIndex;

    createImageUploadCard(colDiv, nextForm, false);
    container.appendChild(colDiv);

    currentSecondaryCount++;
    updateImageCounter();
    updateAddButton();

    console.log(`Aggiunta immagine secondaria ${formIndex}`, {
    currentSecondaryCount,
    activeFormIndices: Array.from(activeFormIndices)
});
}
}

    function removeSecondaryImage(card, deleteInput) {
    const formIndex = parseInt(card.dataset.formIndex);
    const form = document.querySelector(`.formset-form[data-form-index="${formIndex}"]`);
    const colDiv = card.closest('.col-md-4');

    if (form) {
    // Marca per eliminazione se esiste nel DB, altrimenti reset completo
    if (deleteInput) {
    deleteInput.checked = true;
}

    // Reset dei campi
    const inputs = form.querySelectorAll('input');
    inputs.forEach(input => {
    if (input.type === 'file') {
    input.value = '';
} else if (input.type === 'text') {
    input.value = '';
} else if (input.name.includes('is_main')) {
    input.checked = false;
}
});

    // Rimuovi dall'insieme degli attivi
    activeFormIndices.delete(formIndex);
}

    colDiv.remove();
    currentSecondaryCount--;
    updateImageCounter();
    updateAddButton();

    console.log(`Rimossa immagine secondaria ${formIndex}`, {
    currentSecondaryCount,
    activeFormIndices: Array.from(activeFormIndices)
});
}

    function updateImageCounter() {
    const counter = document.getElementById('image-counter');
    counter.textContent = `${currentSecondaryCount}/${MAX_SECONDARY_IMAGES}`;
}

    function updateAddButton() {
    const addBtn = document.getElementById('add-image-btn');
    if (currentSecondaryCount >= MAX_SECONDARY_IMAGES) {
    addBtn.disabled = true;
    addBtn.innerHTML = '<i class="fas fa-check"></i> Limite raggiunto';
} else {
    addBtn.disabled = false;
    addBtn.innerHTML = '<i class="fas fa-plus"></i> Aggiungi Immagine';
}
}

    // Aggiorna il management form prima del submit
    document.querySelector('form').addEventListener('submit', function(e) {
    const totalFormsInput = document.getElementById('id_productimage_set-TOTAL_FORMS');
    const initialFormsInput = document.getElementById('id_productimage_set-INITIAL_FORMS');

    // Conta i form che hanno effettivamente dati o sono marcati per eliminazione
    let actualFormCount = 0;
    const allForms = document.querySelectorAll('.formset-form');

    allForms.forEach((form, index) => {
    const formIndex = parseInt(form.dataset.formIndex);
    const imageInput = form.querySelector('input[type="file"]');
    const deleteInput = form.querySelector('input[name*="DELETE"]');

    // Conta il form se:
    // - Ha un'immagine caricata, O
    // - È marcato per eliminazione (quindi esisteva già)
    if ((imageInput && imageInput.files && imageInput.files.length > 0) ||
    (deleteInput && deleteInput.checked)) {
    actualFormCount++;
}
});

    // Assicurati che almeno il form principale sia contato
    if (actualFormCount === 0) {
    const mainImageInput = document.querySelector('.formset-form[data-form-index="0"] input[type="file"]');
    if (mainImageInput) {
    actualFormCount = 1;
}
}

    totalFormsInput.value = Math.max(actualFormCount, activeFormIndices.size);

    console.log('Submit form:', {
    totalForms: totalFormsInput.value,
    initialForms: initialFormsInput.value,
    activeFormIndices: Array.from(activeFormIndices),
    actualFormCount: actualFormCount
});

    // Debug: stampa tutti i dati del form prima dell'invio
    const formData = new FormData(e.target);
    console.log('FormData contents:');
    for(let pair of formData.entries()) {
    console.log(pair[0] + ': ' + pair[1]);
}
});
});