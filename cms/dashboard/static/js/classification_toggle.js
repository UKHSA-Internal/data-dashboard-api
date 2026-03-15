;(function () {
  function toggleClassification() {
    /*
        When the is_public box is checked, this will clear any selected page_classification, 
        and disable the field. If the is_public box is then unchecked, it will re-enable the field
         */
    const isPublicCheckbox = document.querySelector('input[name="is_public"]')
    const classificationField = document.querySelector(
      'select[name="page_classification"]',
    )

    if (!isPublicCheckbox || !classificationField) return

    if (isPublicCheckbox.checked) {
      classificationField.value = ""
      classificationField.disabled = true
    } else {
      classificationField.disabled = false
    }
  }

  document.addEventListener("DOMContentLoaded", toggleClassification)
  document.addEventListener("change", function (e) {
    if (e.target.name === "is_public") {
      toggleClassification()
    }
  })
})()
