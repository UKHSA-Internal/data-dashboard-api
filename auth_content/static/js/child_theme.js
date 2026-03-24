(function () {
  "use strict";
  let theme, subTheme, topic, metric, geographyType, geography;

  /**
   * Generic function to fetch choices from the API
   * @param {string} endpoint - The API endpoint (e.g., 'subthemes', 'topics', 'metrics')
   * @param {string} dataItemId - The ID value to pass
   * @returns {Promise<Array>} Array of choices [[id, name], ...]
   */
  async function fetchChoices(endpoint, dataItemId) {
    try {
      const url = `/api/permission-set/${endpoint}/${dataItemId}`;
      console.log(`Fetching from: ${url}`);

      const response = await fetch(url);

      if (!response.ok) {
        const errorData = await response.json();
        console.error(`API error: ${errorData.error || "Unknown error"}`);
        return [];
      }

      const data = await response.json();
      console.log(`Received data from ${endpoint}:`, data);
      return data.choices || [];
    } catch (error) {
      console.error(`Error fetching ${endpoint}:`, error);
      return [];
    }
  }
  async function fetchGeographies(endpoint, dataItemId) {
    console.log("selected geography type: ", dataItemId);
    console.log("selected endpoint: ", endpoint);
    try {
      const url = `/api/permission-set/${endpoint}/${dataItemId}`;
      console.log(`Fetching from: ${url}`);

      const response = await fetch(url);

      if (!response.ok) {
        const errorData = await response.json();
        console.error(`API error: ${errorData.error || "Unknown error"}`);
        return [];
      }

      const data = await response.json();
      console.log(`Received data from ${endpoint}:`, data);
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
    wildcardOption.value = "-1";
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

    console.log(`Cleared ${dropdown.name}: ${message}`);
  }

  /**
   * Set dropdown to wildcard and disable it
   * Used when parent is wildcard, cascading "all" to children
   */
  function setToWildcard(
    dropdown,
    message = "* (All - inherited from parent)",
  ) {
    dropdown.innerHTML = "";

    const option = document.createElement("option");
    option.value = "-1";
    option.textContent = message;
    dropdown.appendChild(option);

    dropdown.value = "-1";
  }

  /**
   * Handle theme selection change
   */
  async function handleThemeChange() {
    const themeValue = theme.value;

    // Clear all dependent dropdowns
    if (!themeValue || themeValue === "") {
      console.log("No theme selected - clearing all children");
      clearDropdown(subTheme, "Select theme first");
      clearDropdown(topic, "Select sub-theme first");
      clearDropdown(metric, "Select topic first");
      return;
    }

    if (themeValue === "-1") {
      console.log("Wildcard theme selected - cascading to all children");
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
    console.log("Sub-theme changed to:", subThemeValue);

    if (!subThemeValue || subThemeValue === "") {
      // No sub-theme selected - clear children
      clearDropdown(topic, "Select sub-theme first");
      clearDropdown(metric, "Select topic first");
      return;
    }

    if (subThemeValue === "-1") {
      // Wildcard sub-theme = cascade wildcard to children
      console.log("Wildcard sub-theme selected - cascading to children");
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
    console.log("Topic changed to:", topicValue);

    if (!topicValue || topicValue === "") {
      // No topic selected - clear metrics
      console.log("No topic selected - clearing metrics");
      clearDropdown(metric, "Select topic first");
      return;
    }

    if (topicValue === "-1") {
      // Wildcard topic = cascade wildcard to metrics
      console.log("Wildcard topic selected - cascading to metrics");
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
    console.log("geography type changed to:", geographyTypeValue);

    if (!geographyTypeValue || geographyTypeValue === "") {
      // No topic selected - clear metrics
      console.log("No geography type selected");
      clearDropdown(geography, "Select geography type first");
      return;
    }

    if (geographyTypeValue === "-1") {
      // Wildcard topic = cascade wildcard to metrics
      console.log("Wildcard geography selected - cascading to metrics");
      setToWildcard(geography, "* (All geographies)");
      return;
    }
    clearDropdown(geography, "--------");

    // Fetch and populate metrics
    const choices = await fetchGeographies("geographies", geographyTypeValue);

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
    console.log("Initializing edit mode...");

    // Store original values before we start manipulating dropdowns
    const savedTheme = theme.value;
    const savedSubTheme = subTheme.value;
    const savedTopic = topic.value;
    const savedMetric = metric.value;
    const savedGeographyType = geographyType.value;
    const savedGeography = geography.value;

    console.log("Saved values:", {
      theme: savedTheme,
      subTheme: savedSubTheme,
      topic: savedTopic,
      metric: savedMetric,
      geographyType: savedGeographyType,
      geography: savedGeography,
    });

    // If theme has a value (not wildcard, not empty), load sub-themes
    if (savedTheme && savedTheme !== "" && savedTheme !== "-1") {
      console.log(`Loading sub-themes for theme ${savedTheme}...`);
      const subThemeChoices = await fetchChoices("subthemes", savedTheme);
      if (subThemeChoices.length > 0) {
        populateDropdown(subTheme, subThemeChoices, "* (All sub-themes)");
        subTheme.value = savedSubTheme; // Restore selection
      }

      // If sub-theme has a value, load topics
      if (savedSubTheme && savedSubTheme !== "" && savedSubTheme !== "-1") {
        console.log(`Loading topics for sub-theme ${savedSubTheme}...`);
        const topicChoices = await fetchChoices("topics", savedSubTheme);
        if (topicChoices.length > 0) {
          populateDropdown(topic, topicChoices, "* (All topics)");
          topic.value = savedTopic; // Restore selection
        }

        // If topic has a value, load metrics
        if (savedTopic && savedTopic !== "" && savedTopic !== "-1") {
          console.log(`Loading metrics for topic ${savedTopic}...`);
          const metricChoices = await fetchChoices("metrics", savedTopic);
          if (metricChoices.length > 0) {
            populateDropdown(metric, metricChoices, "* (All metrics)");
            metric.value = savedMetric; // Restore selection
          }
        }
      }
    } else if (savedTheme === "-1") {
      // Theme is wildcard, cascade to children
      setToWildcard(subTheme, "* (All sub-themes)");
      setToWildcard(topic, "* (All topics)");
      setToWildcard(metric, "* (All metrics)");
    }

    // Handle geography independently
    if (
      savedGeographyType &&
      savedGeographyType !== "" &&
      savedGeographyType !== "-1"
    ) {
      console.log(
        `Loading geographies for geography type ${savedGeographyType}...`,
      );
      const geographyChoices = await fetchChoices(
        "geographies",
        savedGeographyType,
      );
      if (geographyChoices.length > 0) {
        populateDropdown(geography, geographyChoices, "* (All geographies)");
        geography.value = savedGeography; // Restore selection
      }
    } else if (savedGeographyType === "-1") {
      setToWildcard(geography, "* (All geographies)");
    }

    console.log("Edit mode initialization complete");
  }

  /**
   * Initialize the cascading dropdowns
   */
  function initialize() {
    console.log("Initializing...");

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
      console.log("Permission set dropdowns not found on this page");
      return;
    }

    // Add event listeners
    theme.addEventListener("change", handleThemeChange);
    subTheme.addEventListener("change", handleSubThemeChange);
    topic.addEventListener("change", handleTopicChange);
    geographyType.addEventListener("change", handleGeographyTypeChange);

    console.log("Event listeners attached");
    const isEditMode =
      theme.value ||
      subTheme.value ||
      topic.value ||
      metric.value ||
      geographyType.value ||
      geography.value;

    if (isEditMode) {
      console.log("Edit mode detected");
      initializeEditMode();
    } else {
      console.log("Create mode - setting initial state");
      clearDropdown(subTheme, "Select theme first");
      clearDropdown(topic, "Select sub-theme first");
      clearDropdown(metric, "Select topic first");
      clearDropdown(geography, "Select geography type first");
    }
  }

  // Initialize when DOM is ready
  document.addEventListener("DOMContentLoaded", initialize);
})();
