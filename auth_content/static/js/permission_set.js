(function () {
  "use strict";
  let theme, subTheme, topic, metric, geographyType, geography;
  const WILDCARD_ID_VALUE = "-1";

  /**
   * Generic function to fetch choices from the API
   * @param {string} endpoint - The API endpoint (e.g., 'subthemes', 'topics', 'metrics', 'geography')
   * @param {string} dataItemId - The ID value to pass
   * @returns {Promise<Array>} Array of choices [[id, name], ...]
   */
  async function fetchChoices(endpoint, dataItemId) {
    try {
      const url = `/api/data-hierarchy/${endpoint}/${dataItemId}`;

      const response = await fetch(url);

      if (!response.ok) {
        const errorData = await response.json();
        console.error(`API error: ${errorData.error || "Unknown error"}`);
        return [];
      }

      const data = await response.json();
      return data.choices || [];
    } catch (error) {
      console.error(`Error fetching ${endpoint}:`, error);
      return [];
    }
  }

  /**
   * Generic function to populate a dropdown with choices
   * @param {HTMLSelectElement} dropdown - The select element to populate
   * @param {Array} choices - Array of [id, name] tuples
   */
  function populateDropdown(dropdown, choices, wildcardValue = "* All Items") {
    const currentValue = dropdown.value;
    dropdown.disabled = false;
    dropdown.innerHTML = "";

    //dropdown empty
    const nullOption = document.createElement("option");
    nullOption.value = "";
    nullOption.textContent = "--------";
    dropdown.appendChild(nullOption);

    //dropdown wildcard choice
    const wildcardOption = document.createElement("option");
    wildcardOption.value = WILDCARD_ID_VALUE;
    wildcardOption.textContent = wildcardValue;
    dropdown.appendChild(wildcardOption);

    choices.forEach(([id, name]) => {
      const option = document.createElement("option");
      option.value = id;
      option.textContent = name;
      dropdown.appendChild(option);
    });

    if (currentValue) {
      dropdown.value = currentValue;
    }
  }

  function clearDropdown(dropdown, message = "Select parent first") {
    dropdown.innerHTML = "";

    const option = document.createElement("option");
    option.value = "";
    option.textContent = message;
    dropdown.appendChild(option);

    dropdown.value = "";
  }

  /**
   * Set dropdown to wildcard and disable it
   * Used when parent is wildcard, cascading "all" to children
   * @param {string} dropdown - The name of the option element that should be updated with the wildcard option.
   * @param {string} message - Message to display in the dropdown menu
   * @returns {Promise<Array>} Array of choices [[id, name], ...]
   */
  function setToWildcard(
    dropdown,
    message = "* (All - inherited from parent)",
  ) {
    dropdown.innerHTML = "";

    const option = document.createElement("option");
    option.value = WILDCARD_ID_VALUE;
    option.textContent = message;
    dropdown.appendChild(option);

    dropdown.value = WILDCARD_ID_VALUE;
  }

  /**
   * Handle theme selection change
   */
  async function handleThemeChange() {
    const themeValue = theme.value;

    // Clear all dependent dropdowns
    if (!themeValue || themeValue === "") {
      clearDropdown(subTheme, "Select theme first");
      clearDropdown(topic, "Select sub-theme first");
      clearDropdown(metric, "Select topic first");
      return;
    }

    if (themeValue === WILDCARD_ID_VALUE) {
      setToWildcard(subTheme, "* (All sub-themes)");
      setToWildcard(topic, "* (All topics)");
      setToWildcard(metric, "* (All metrics)");
      return;
    }

    clearDropdown(subTheme, "--------");
    clearDropdown(topic, "--------");
    clearDropdown(metric, "--------");

    // Fetch and populate sub-themes
    const choices = await fetchChoices("subthemes", themeValue);

    if (choices.length > 0) {
      populateDropdown(subTheme, choices, "* All sub-themes");
    } else {
      clearDropdown(subTheme, "No sub-themes available");
    }
  }

  /**
   * Handle sub-theme selection change
   */
  async function handleSubThemeChange() {
    const subThemeValue = subTheme.value;

    if (!subThemeValue || subThemeValue === "") {
      // No sub-theme selected - clear children
      clearDropdown(topic, "Select sub-theme first");
      clearDropdown(metric, "Select topic first");
      return;
    }

    if (subThemeValue === WILDCARD_ID_VALUE) {
      // Wildcard sub-theme = cascade wildcard to children
      setToWildcard(topic, "* (All topics)");
      setToWildcard(metric, "* (All metrics)");
      return;
    }

    // Clear dependent dropdowns
    clearDropdown(topic, "Select sub-theme");
    clearDropdown(metric, "Select metric");

    // Fetch and populate topics
    const choices = await fetchChoices("topics", subThemeValue);

    if (choices.length > 0) {
      populateDropdown(topic, choices, "* All topics");
    } else {
      clearDropdown(topic, "No topics available");
    }
  }

  /**
   * Handle topic selection change
   */
  async function handleTopicChange() {
    const topicValue = topic.value;

    if (!topicValue || topicValue === "") {
      // No topic selected - clear metrics
      clearDropdown(metric, "Select topic first");
      return;
    }

    if (topicValue === WILDCARD_ID_VALUE) {
      // Wildcard topic = cascade wildcard to metrics
      setToWildcard(metric, "* (All metrics)");
      return;
    }

    clearDropdown(metric, "--------");

    // Fetch and populate metrics
    const choices = await fetchChoices("metrics", topicValue);

    if (choices.length > 0) {
      populateDropdown(metric, choices, "* All metrics");
    } else {
      clearDropdown(metric, "No metrics available");
    }
  }
  async function handleGeographyTypeChange() {
    const geographyTypeValue = geographyType.value;

    if (!geographyTypeValue || geographyTypeValue === "") {
      // No topic selected - clear metrics
      clearDropdown(geography, "Select geography type first");
      return;
    }

    if (geographyTypeValue === WILDCARD_ID_VALUE) {
      // Wildcard topic = cascade wildcard to metrics
      setToWildcard(geography, "* (All geographies)");
      return;
    }
    clearDropdown(geography, "--------");

    // Fetch and populate metrics
    const choices = await fetchChoices("geographies", geographyTypeValue);

    if (choices.length > 0) {
      populateDropdown(geography, choices, "* All geographies");
    } else {
      clearDropdown(geography, "No geographies available");
    }
  }

  /**
   * Initialize dropdowns for edit mode
   * Loads the dropdown options based on saved values
   */
  async function initializeEditMode() {
    // Store original values before we start manipulating dropdowns
    const savedTheme = theme.value;
    const savedSubTheme = subTheme.value;
    const savedTopic = topic.value;
    const savedMetric = metric.value;
    const savedGeographyType = geographyType.value;
    const savedGeography = geography.value;

    // If theme has a value (not wildcard, not empty), load sub-themes
    if (savedTheme && savedTheme !== "" && savedTheme !== WILDCARD_ID_VALUE) {
      const subThemeChoices = await fetchChoices("subthemes", savedTheme);
      if (subThemeChoices.length > 0) {
        populateDropdown(subTheme, subThemeChoices, "* (All sub-themes)");
        subTheme.value = savedSubTheme; // Restore selection
      }

      // If sub-theme has a value, load topics
      if (
        savedSubTheme &&
        savedSubTheme !== "" &&
        savedSubTheme !== WILDCARD_ID_VALUE
      ) {
        const topicChoices = await fetchChoices("topics", savedSubTheme);
        if (topicChoices.length > 0) {
          populateDropdown(topic, topicChoices, "* (All topics)");
          topic.value = savedTopic; // Restore selection
        }

        // If topic has a value, load metrics
        if (
          savedTopic &&
          savedTopic !== "" &&
          savedTopic !== WILDCARD_ID_VALUE
        ) {
          const metricChoices = await fetchChoices("metrics", savedTopic);
          if (metricChoices.length > 0) {
            populateDropdown(metric, metricChoices, "* (All metrics)");
            metric.value = savedMetric; // Restore selection
          }
        }
      }
    } else if (savedTheme === WILDCARD_ID_VALUE) {
      // Theme is wildcard, cascade to children
      setToWildcard(subTheme, "* (All sub-themes)");
      setToWildcard(topic, "* (All topics)");
      setToWildcard(metric, "* (All metrics)");
    }

    // Handle geography independently
    if (
      savedGeographyType &&
      savedGeographyType !== "" &&
      savedGeographyType !== WILDCARD_ID_VALUE
    ) {
      const geographyChoices = await fetchChoices(
        "geographies",
        savedGeographyType,
      );
      if (geographyChoices.length > 0) {
        populateDropdown(geography, geographyChoices, "* (All geographies)");
        geography.value = savedGeography; // Restore selection
      }
    } else if (savedGeographyType === WILDCARD_ID_VALUE) {
      setToWildcard(geography, "* (All geographies)");
    }
  }

  /**
   * Initialize the cascading dropdowns
   */
  function initialize() {
    // Get dropdown elements
    theme = document.querySelector('select[name="theme"]');
    subTheme = document.querySelector('select[name="sub_theme"]');
    topic = document.querySelector('select[name="topic"]');
    metric = document.querySelector('select[name="metric"]');
    geographyType = document.querySelector('select[name="geography_type"]');
    geography = document.querySelector('select[name="geography"]');

    // Exit if not on permission set page
    if (
      !theme ||
      !subTheme ||
      !topic ||
      !metric ||
      !geographyType ||
      !geography
    ) {
      console.error("Permission set dropdowns not found on this page");
      return;
    }

    // Add event listeners
    theme.addEventListener("change", handleThemeChange);
    subTheme.addEventListener("change", handleSubThemeChange);
    topic.addEventListener("change", handleTopicChange);
    geographyType.addEventListener("change", handleGeographyTypeChange);

    const isEditMode =
      theme.value ||
      subTheme.value ||
      topic.value ||
      metric.value ||
      geographyType.value ||
      geography.value;

    if (isEditMode) {
      initializeEditMode();
    } else {
      clearDropdown(subTheme, "Select theme first");
      clearDropdown(topic, "Select sub-theme first");
      clearDropdown(metric, "Select topic first");
      clearDropdown(geography, "Select geography type first");
    }
  }

  // Initialize when DOM is ready
  document.addEventListener("DOMContentLoaded", initialize);
})();