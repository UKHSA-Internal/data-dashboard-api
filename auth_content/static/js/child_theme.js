(function () {
  "use strict";

  console.log("Permission set cascading script loaded");

  let theme, subTheme, topic, metric;

  /**
   * Generic function to fetch choices from the API
   * @param {string} endpoint - The API endpoint (e.g., 'subthemes', 'topics', 'metrics')
   * @param {string} paramValue - The ID value to pass
   * @returns {Promise<Array>} Array of choices [[id, name], ...]
   */
  async function fetchChoices(endpoint, paramValue) {
    try {
      const url = `/api/permission-set/${endpoint}/${paramValue}`;
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

    console.log(`Populated ${dropdown.name} with ${choices.length} options`);
  }

  /**
   * Generic function to clear and disable a dropdown
   * @param {HTMLSelectElement} dropdown - The select element to clear
   * @param {string} message - Message to display
   */
  function clearDropdown(dropdown, message = "Select parent first") {
    dropdown.innerHTML = "";

    const option = document.createElement("option");
    option.value = "-1";
    option.textContent = message;
    dropdown.appendChild(option);

    dropdown.value = "-1";
    dropdown.disabled = true;

    console.log(`Cleared ${dropdown.name}: ${message}`);
  }

  /**
   * Handle theme selection change
   */
  async function handleThemeChange() {
    const themeValue = theme.value;
    console.log("Theme changed to:", themeValue);

    // Clear all dependent dropdowns
    clearDropdown(subTheme, "Loading...");
    clearDropdown(topic, "Select sub-theme first");
    clearDropdown(metric, "Select topic first");

    if (themeValue === "-1") {
      console.log("Wildcard theme selected");
      clearDropdown(subTheme, "Select theme first");
      return;
    }

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

    // Clear dependent dropdowns
    clearDropdown(topic, "Loading...");
    clearDropdown(metric, "Select topic first");

    if (subThemeValue === "-1") {
      console.log("Wildcard or no sub-theme selected");
      clearDropdown(topic, "Select sub-theme first");
      return;
    }

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

    clearDropdown(metric, "Loading...");

    if (topicValue === "-1") {
      console.log("Wildcard or no topic selected");
      clearDropdown(metric, "Select topic first");
      return;
    }

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

    console.log("Found all dropdowns: theme, sub_theme, topic, metric");

    // Set initial disabled state
    clearDropdown(subTheme, "Select theme first");
    clearDropdown(topic, "Select sub-theme first");
    clearDropdown(metric, "Select topic first");

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
