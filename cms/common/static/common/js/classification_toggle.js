
(function() {
    function toggleClassification() {
        const isPublicCheckbox = document.querySelector('input[name="is_public"]');
        const classificationField = document.querySelector('select[name="page_classification"]');

        if (!isPublicCheckbox || !classificationField) return;

        if (isPublicCheckbox.checked) {
            classificationField.value = "";
            classificationField.disabled = true;
        } else {
            classificationField.disabled = false;
        }
    }

    document.addEventListener("DOMContentLoaded", toggleClassification);
    document.addEventListener("change", function(e) {
        if (e.target.name === "is_public") {
            toggleClassification();
        }
    });
})();
