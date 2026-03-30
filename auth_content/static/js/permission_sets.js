;(function () {
  "use strict"

  /**
   * Fetch choices from the PermissionSet API endpoint.
   */
  async function fetchPermissionSets() {
    try {
      const url = "/api/permission-set/all"

      const response = await fetch(url)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        console.error(
          `Permission Set API error: ${errorData.error || "Unknown error"}`,
        )
        return []
      }

      const data = await response.json()
      return data.choices || []
    } catch (error) {
      console.error("Error fetching permission sets:", error)
      return []
    }
  }

  /**
   * Populate a dropdown <select> with permission set choices.
   */
  function populatePermissionSetDropdown(dropdown, choices) {
    const currentValue = dropdown.value
    const usedValues = getSelectedPermissionSetValues()

    dropdown.disabled = false
    dropdown.innerHTML = ""

    // Default empty choice
    const emptyOption = document.createElement("option")
    emptyOption.value = ""
    emptyOption.textContent = "---------"
    dropdown.appendChild(emptyOption)

    // Populate dynamic permission sets
    choices.forEach(([id, name]) => {
      const opt = document.createElement("option")
      opt.value = id
      opt.textContent = name

      if (usedValues.includes(id) && id !== currentValue) {
        opt.disabled = true
        opt.textContent = `${name} (already selected)`
      }

      dropdown.appendChild(opt)
    })

    // Restore previous value (if any)
    if (currentValue) {
      dropdown.value = currentValue
    }
  }

  /**
   * Find all PermissionSet selects inside StreamField blocks.
   */
  function findAllPermissionSetDropdowns() {
    return document.querySelectorAll('select[name$="-value"]')
  }

  /**
   * Populate all dropdowns on the page
   */
  async function populateAllDropdowns() {
    const selects = findAllPermissionSetDropdowns()
    if (selects.length === 0) {
      return
    }

    const choices = await fetchPermissionSets()

    selects.forEach((select) => {
      populatePermissionSetDropdown(select, choices)
    })
  }

  /**
   * StreamField creates new blocks dynamically.
   * We observe DOM changes to catch new block insertions
   * and populate the dropdown inside new blocks.
   */
  function observeStreamFieldChanges() {
    const observer = new MutationObserver(async (mutations) => {
      for (const mutation of mutations) {
        if (mutation.addedNodes.length > 0) {
          const selects = []

          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE) {
              // Case 1: the node itself is a select
              if (node.matches && node.matches("select[name$='-value']")) {
                selects.push(node)
              }

              // Case 2: the node contains the select
              const innerSelects = node.querySelectorAll
                ? node.querySelectorAll('select[name$="-value"]')
                : []
              innerSelects.forEach((el) => selects.push(el))
            }
          })

          if (selects.length > 0) {
            const choices = await fetchPermissionSets()
            selects.forEach((select) =>
              populatePermissionSetDropdown(select, choices),
            )
          }
        }
      }
    })

    observer.observe(document.body, {
      subtree: true,
      childList: true,
    })
  }

  function getSelectedPermissionSetValues() {
    return Array.from(document.querySelectorAll('select[name$="-value"]'))
      .map((selected) => selected.value)
      .filter((value) => value !== "")
  }

  /**
   * Initialize once DOM is ready
   */
  function initialize() {
    // Initial population
    populateAllDropdowns()

    // Handle StreamField block insertions
    observeStreamFieldChanges()
  }

  document.addEventListener("DOMContentLoaded", initialize)
})()
