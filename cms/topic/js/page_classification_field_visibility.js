(function () {
    function toggleClassification() {
        const isPublicCheckbox = document.querySelector('#id_is_public');
        const classificationField = document.querySelector('#id_page_classification')
            .closest('.w-field');  // wrapper div Wagtail uses

        if (isPublicCheckbox.checked) {
            classificationField.style.display = '';
        } else {
            classificationField.style.display = 'none';
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        const isPublicCheckbox = document.querySelector('#id_is_public');
        if (!isPublicCheckbox) return;

        // Apply initially
        toggleClassification();

        // Update when toggled
        isPublicCheckbox.addEventListener('change', toggleClassification);
    });
})();
``