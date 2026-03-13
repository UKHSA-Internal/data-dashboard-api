;(function () {
  let theme,
    sub_theme,
    themeMapping = {}

  function setSubTheme() {
    theme = document.querySelector('select[name="theme"]')
    sub_theme = document.querySelector('select[name="sub_theme"]')

    if (!theme || !sub_theme) return

    try {
      themeMapping = window.PERMISSIONSET_THEME_MAP
    } catch (e) {
      console.error("Invalid theme map")
    }

    if (!theme.value) {
      clearSubTheme()
    } else {
      populateSubThemeDropDown()
    }
  }
  function populateSubThemeDropDown() {
    sub_theme.disabled = false
    sub_theme.innerHTML = ""
    sub_theme.add(new Option("---------", ""))

    const options = themeMapping[theme.value] || []

    options.forEach(([value, label]) => sub_theme.add(new Option(label, value)))
  }

  function clearSubTheme() {
    sub_theme.innerHTML = ""
    sub_theme.add(new Option("---------", ""))
    sub_theme.value = ""
    sub_theme.disabled = true
  }

  document.addEventListener("DOMContentLoaded", setSubTheme)
  document.addEventListener("change", function (e) {
    if (e.target.name === "theme") {
      setSubTheme()
    }
  })
})()
