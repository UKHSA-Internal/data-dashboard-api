(function () {
  let theme,
    sub_theme,
    topic,
    subThemeMapping = {},
    themeMapping = {};

  function setSubTheme() {
    theme = document.querySelector('select[name="theme"]');
    sub_theme = document.querySelector('select[name="sub_theme"]');

    if (!theme || !sub_theme) return;

    themeMapping = window.PERMISSIONSET_THEME_MAP;

    if (!theme.value) {
      clearSubTheme();
    } else {
      populateSubThemeDropDown();
    }
  }

  function setTopic() {
    sub_theme = document.querySelector('select[name="sub_theme"]');
    topic = document.querySelector('select[name="topic"]');

    if (!sub_theme || !topic) return;

    subThemeMapping = window.PERMISSIONSET_SUB_THEME_MAP;
    console.log("subTheme: ", subThemeMapping);

    console.log(sub_theme.value);

    if (!sub_theme.value) {
      clearTopic();
    } else {
      populateTopicDropDown();
    }
  }

  function populateSubThemeDropDown() {
    sub_theme.disabled = false;
    sub_theme.innerHTML = "";
    sub_theme.add(new Option("---------", ""));

    const options = themeMapping[theme.value] || [];

    options.forEach(([value, label]) =>
      sub_theme.add(new Option(label, value)),
    );
  }

  function clearSubTheme() {
    sub_theme.innerHTML = "";
    sub_theme.add(new Option("---------", ""));
    sub_theme.value = "";
    sub_theme.disabled = true;
  }

  function populateTopicDropDown() {
    topic.disabled = false;
    topic.innerHTML = "";
    topic.add(new Option("---------", ""));

    const options = subThemeMapping[sub_theme.value] || [];
    console.log("options:", subThemeMapping);

    options.forEach(([value, label]) => topic.add(new Option(label, value)));
  }

  function clearTopic() {
    topic.innerHTML = "";
    topic.add(new Option("---------", ""));
    topic.value = "";
    topic.disabled = true;
  }

  document.addEventListener("DOMContentLoaded", setSubTheme);
  document.addEventListener("DOMContentLoaded", setTopic);

  document.addEventListener("change", function (e) {
    if (e.target.name === "theme") {
      setSubTheme();
    }
    if (e.target.name === "sub_theme") {
      setTopic();
    }
  });
})();
