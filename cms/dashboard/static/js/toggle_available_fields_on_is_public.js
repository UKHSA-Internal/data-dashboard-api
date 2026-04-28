;(function () {
  function toggleAvailableFields() {
    /*
        When the is_public box is checked, this will clear any selected page_classification, 
        and disable the field. If the is_public box is then unchecked, it will re-enable the field
         */
    const isPublicCheckbox = document.querySelector('input[name="is_public"]')

    const fields = {
      classification: document.querySelector(
        'select[name="page_classification"]',
      ),
      theme: document.querySelector('select[name="theme"]'),
      subTheme: document.querySelector('select[name="sub_theme"]'),
      topic: document.querySelector('select[name="topic"]'),
    }

    if (!isPublicCheckbox || !Object.values(fields).every(Boolean)) return

    if (isPublicCheckbox.checked) {
      Object.values(fields).forEach(disableField)
    } else {
      Object.values(fields).forEach(enableField)
    }
  }

  function disableField(field) {
    field.value = ""
    field.disabled = true
  }

  function enableField(field) {
    field.disabled = false
  }

  document.addEventListener("DOMContentLoaded", toggleAvailableFields)
  document.addEventListener("change", function (e) {
    if (e.target.name === "is_public") {
      toggleAvailableFields()
    }
  })
})()
