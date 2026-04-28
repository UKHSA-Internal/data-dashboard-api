;(function () {
  "use strict"
  let theme, subTheme, topic

  /**
   * Generic function to fetch choices from the API
   * @param {string} endpoint - The API endpoint (e.g., 'subthemes', 'topics')
   * @param {string} dataItemId - The ID value to pass
   * @returns {Promise<Array>} Array of choices [[id, name], ...]
   */
  async function fetchChoices(endpoint, dataItemId) {
    try {
      const url = `/api/data-hierarchy/${endpoint}/${dataItemId}`
      console.log("🦄 fetching choices")
      const response = await fetch(url)

      if (!response.ok) {
        const errorData = await response.json()
        console.error(`API error: ${errorData.error || "Unknown error"}`)
        return []
      }

      const data = await response.json()
      return data.choices || []
    } catch (error) {
      console.error(`Error fetching ${endpoint}:`, error)
      return []
    }
  }

  /**
   * Generic function to populate a dropdown with choices
   * @param {HTMLSelectElement} dropdown - The select element to populate
   * @param {Array} choices - Array of [id, name] tuples
   */
  function populateDropdown(dropdown, choices) {
    const currentValue = dropdown.value
    dropdown.disabled = false
    dropdown.innerHTML = ""

    //dropdown empty
    const nullOption = document.createElement("option")
    nullOption.value = ""
    nullOption.textContent = "--------"
    dropdown.appendChild(nullOption)

    choices.forEach(([id, name]) => {
      const option = document.createElement("option")
      option.value = id
      option.textContent = name
      dropdown.appendChild(option)
    })

    if (currentValue) {
      dropdown.value = currentValue
    }
  }

  function clearDropdown(dropdown, message = "Select parent first") {
    dropdown.innerHTML = ""

    const option = document.createElement("option")
    option.value = ""
    option.textContent = message
    dropdown.appendChild(option)

    dropdown.value = ""
  }

  /**
   * Handle theme selection change
   */
  async function handleThemeChange() {
    const themeValue = theme.value

    // Clear all dependent dropdowns
    if (!themeValue || themeValue === "") {
      clearDropdown(subTheme, "Select theme first")
      clearDropdown(topic, "Select sub-theme first")
      return
    }

    clearDropdown(subTheme, "--------")
    clearDropdown(topic, "--------")

    // Fetch and populate sub-themes
    const choices = await fetchChoices("subthemes", themeValue)

    if (choices.length > 0) {
      populateDropdown(subTheme, choices)
    } else {
      clearDropdown(subTheme, "No sub-themes available")
    }
  }

  /**
   * Handle sub-theme selection change
   */
  async function handleSubThemeChange() {
    const subThemeValue = subTheme.value

    if (!subThemeValue || subThemeValue === "") {
      // No sub-theme selected - clear children
      clearDropdown(topic, "Select sub-theme first")
      return
    }

    // Clear dependent dropdowns
    clearDropdown(topic, "Select sub-theme")

    // Fetch and populate topics
    const choices = await fetchChoices("topics", subThemeValue)

    if (choices.length > 0) {
      populateDropdown(topic, choices)
    } else {
      clearDropdown(topic, "No topics available")
    }
  }

  /**
   * Initialize dropdowns for edit mode
   * Loads the dropdown options based on saved values
   */
  async function initializeEditMode() {
    // Store original values before we start manipulating dropdowns
    const savedTheme = theme.value
    const savedSubTheme = subTheme.value
    const savedTopic = topic.value

    // If theme has a value (not empty), load sub-themes
    if (savedTheme && savedTheme !== "") {
      const subThemeChoices = await fetchChoices("subthemes", savedTheme)
      if (subThemeChoices.length > 0) {
        populateDropdown(subTheme, subThemeChoices)
        subTheme.value = savedSubTheme // Restore selection
      }

      // If sub-theme has a value, load topics
      if (savedSubTheme && savedSubTheme !== "") {
        const topicChoices = await fetchChoices("topics", savedSubTheme)
        if (topicChoices.length > 0) {
          populateDropdown(topic, topicChoices)
          topic.value = savedTopic // Restore selection
        }
      }
    }
  }

  /**
   * Initialize the cascading dropdowns
   */
  function initialize() {
    // Get dropdown elements
    theme = document.querySelector('select[name="theme"]')
    subTheme = document.querySelector('select[name="sub_theme"]')
    topic = document.querySelector('select[name="topic"]')

    // Exit if not on permission set page
    if (!theme || !subTheme || !topic) {
      console.error("No theme dropdowns found on this page")
      return
    }

    // Add event listeners
    theme.addEventListener("change", handleThemeChange)
    subTheme.addEventListener("change", handleSubThemeChange)

    const isEditMode = theme.value || subTheme.value || topic.value

    if (isEditMode) {
      initializeEditMode()
    } else {
      clearDropdown(subTheme, "Select theme first")
      clearDropdown(topic, "Select sub-theme first")
    }
  }

  // Initialize when DOM is ready
  document.addEventListener("DOMContentLoaded", initialize)
})()
