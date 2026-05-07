/**
 * @jest-environment jsdom
 */

const { setToWildcard, WILDCARD_ID_VALUE } = require("./permission_set.js");

describe("setToWildcard", () => {
  test("sets dropdown to wildcard state correctly", () => {
    // Arrange: create a fake select element
    const select = document.createElement("select");

    // Add some existing options to ensure it gets cleared
    const oldOption = document.createElement("option");
    oldOption.value = "123";
    oldOption.textContent = "Old";
    select.appendChild(oldOption);
    select.value = "123";

    // Act
    setToWildcard(select, "* All Items");

    // Assert
    expect(select.children.length).toBe(1);

    const option = select.children[0];
    expect(option.value).toBe(WILDCARD_ID_VALUE);
    expect(option.textContent).toBe("* All Items");
    expect(select.value).toBe(WILDCARD_ID_VALUE);
  });
});