(function () {
  "use strict";
  let theme, subTheme, topic, metric;

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

  /**
   * Generic function to populate a dropdown with choices
   * @param {HTMLSelectElement} dropdown - The select element to populate
   * @param {Array} choices - Array of [id, name] tuples
   */
  function populateDropdown(dropdown, choices) {
    dropdown.disabled = false;
    dropdown.innerHTML = "";

    choices.forEach(([id, name]) => {
      const option = document.createElement("option");
      option.value = id;
      option.textContent = name;
      dropdown.appendChild(option);
    });
  }

  function clearDropdown(dropdown, message = "Select parent first") {
    dropdown.innerHTML = "";

    const option = document.createElement("option");
    option.value = "";
    option.textContent = message;
    dropdown.appendChild(option);

    dropdown.value = "";
    dropdown.disabled = true;

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
    dropdown.disabled = true;

    console.log(`Set ${dropdown.name} to wildcard: ${message}`);
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
      populateDropdown(subTheme, choices);
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
    clearDropdown(topic, "--------");
    clearDropdown(metric, "--------");

    // Fetch and populate topics
    const choices = await fetchChoices("topics", subThemeValue);

    if (choices.length > 0) {
      populateDropdown(topic, choices);
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
      populateDropdown(metric, choices);
    } else {
      clearDropdown(metric, "No metrics available");
    }
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

    // Exit if not on permission set page
    if (!theme || !subTheme || !topic || !metric) {
      console.log("Permission set dropdowns not found on this page");
      return;
    }

    // Set initial disabled state
    clearDropdown(subTheme, "--------");
    clearDropdown(topic, "--------");
    clearDropdown(metric, "--------");

    // Add event listeners
    theme.addEventListener("change", handleThemeChange);
    subTheme.addEventListener("change", handleSubThemeChange);
    topic.addEventListener("change", handleTopicChange);

    console.log("Event listeners attached");

    // If editing existing record, trigger cascade to repopulate
    if (theme.value && theme.value !== "-1") {
      console.log("Existing theme value detected:", theme.value);
      handleThemeChange().then(() => {
        // After sub-themes load, check if sub-theme was already selected
        setTimeout(() => {
          if (subTheme.value && subTheme.value !== "-1") {
            console.log("Existing sub-theme value detected:", subTheme.value);
            handleSubThemeChange().then(() => {
              // After topics load, check if topic was already selected
              setTimeout(() => {
                if (topic.value && topic.value !== "-1") {
                  console.log("Existing topic value detected:", topic.value);
                  handleTopicChange();
                }
              }, 300);
            });
          }
        }, 300);
      });
    }
  }

  // Initialize when DOM is ready
  document.addEventListener("DOMContentLoaded", initialize);
})();
