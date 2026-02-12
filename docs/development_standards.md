# Development Standards Guide

## Introduction

This document will describe the standards and practices which are to be applied 
and must be adhered to when developing within this codebase.

---

## Testing

### Writing unit tests

This project makes use of `pytest` as the primary test runner.
The Gherkin-style has been adopted for writing unit tests.
Let's say we have a function called `get_geographies()` that we want to test.

We would wrap **all the tests for that function within a test class**.
The test class should be named `Test<FunctionName>` whereby the function name is snake-cased.

And then each method on that test class would represent a single unit test.
The **name of each method would summarise the test**.

For classes we would name the test class after the class itself and group the methods accordingly:
```python
class TestNameOfClass:
    # method_name_one
    def test_method_name_one_does_something:
        ...
    
    # method_name_two
    def test_method_name_two_does_something:
        ...
```

> Note that we do not need to repeat the name of the function within the name of the test method. 
> As that is already encapsulated by the test class

See below for an example of how we might write a unit test for our `get_geographies()` function.

```python
class TestGetGeographies:
    def test_returns_correct_values(self):
        """
        Given a valid `geography_type`  
        When `get_geographies()` is called
        Then a list of correct geography names is returned
        """
        # Given
        geography_type = "Government Office Region"
        
        # When
        retrieved_geographies: List[str] = get_geographies(geography_type=geography_type)
        
        # Then
        expected_geographies = ["London", "Yorkshire and The Humber",]
        assert retrieved_geographies == expected_geographies
```

Each test should declare a docstring with the `Given` `When` `Then` statements.
You may have seen 3 A's before `Arrange` `Act` `Assert`. This is the same concept.

This should help you organize your tests into discrete but recognisable parts.

The statements should follow the below convention:
```
Given <a set of arranged state>
When <the piece of code is executed>
Then <the result should be>
```

The body of the test should also signpost to each of these parts clearly with a comment to state the part:
```python
# Given
geography_type = "Government Office Region"

# When
...
```

Also make note of the **new line break between the end of 1 section and the start of the next**.
This is important as it helps break the test up visually for the reader.

If the line of a given statement is too long, then it is permissible to drop down a line and add a `And` statement.
For example:

```python
def test_returns_correct_values(self):
    """
    Given a valid `geography_type`  
    When `get_geographies()` is called
    Then a list of correct geography names is returned
    And something else should have happened
    """
```

Note that multiple assertions are okay provided they make sense within that context. 
If you feel like your unit test has too many assertions then it is probably worth breaking it up into multiple tests.

> Unit tests should be cheap, quick and reliable to run. They should be in the order of a few milliseconds.

*Unit* tests which take > 100ms are most definitely not drawing the right boundaries and should be revisited.

Note keep in mind that test cases should act as a specification of the system, so if an edge or "special" case is
conditional for a method or function you are testing, make that condition its own test.

An example of this would be formatting file or directory names, the method you are testing may format the names based
on a set of rules around what special characters are allowed or should be removed. However there could be a case where
a name under some condition is changed for an alternative display name. A condition that changes one name to another
would warrant a new test to highlight this requirement in the spec.

```python
class TestFormatFilenames:
    def test_filename_is_formatted_correctly(self):
        ...
    
    def test_dashboard_is_changed_to_landing_page(self):
        ...
```

### Patching in tests

When it comes to patching the following pattern is preferred:

```python
from unittest import mock

MODULE_PATH = "path.to.module"

class TestGetGeographies:
    @mock.patch(f"{MODULE_PATH}.get_regional_geographies")
    def test_delegates_call_to_get_regional_geographies(
            self, spy_get_regional_geographies: mock.MagicMock
    ):
        """
        Given a valid `geography_type`  
        When `get_geographies()` is called
        Then a list of correct geography names is returned
        
        Patches: 
            `spy_get_regional_geographies`: For the main assertion.
                To check the call to fetch local regional 
                geographies is delegated successfully 
        """
        # Given
        geography_type = "Government Office Region"
        
        # When
        get_geographies(geography_type=geography_type)
        
        # Then
        spy_get_regional_geographies.assert_called_once()
```

In this scenario, we will define a `MODULE_PATH` variable at the module level of the test file.
This will reduce repetition and also helps us to move tests around whenever we need to.

The argument pass to the test should be `<mock type>_<function_name>`.
Note that this `mock_type` is dependent on what we are using the test double for.

In general, `spy` suggests that we are checking how something is being called.
Often we need to check the arguments passed to a function or method call.

Another example, would be `mocked` when we are mocking something in order to draw some boundary around our test.

Also note that the test docstring should include a `Patches` section 
which describes the intention behind each patched object.

---

### Writing integration tests

Integration tests tend to involve more steps than unit tests.
As such it is important to ensure the body of the test is signposted with enough comments.

```python
    def test_main_line_plot(self):
        """
        Given a list of Y-axis values
        When `generate_chart_figure()` is called from the `line` module
        Then the figure is drawn with the expected parameters for the main line
        """
        # Given
        y_axis_values = [1, 2, 3, 4, 5,]

        # When
        figure: plotly.graph_objects.Figure = generate_chart_figure(
            chart_height=220,
            chart_width=930,
            y_axis_values=y_axis_values,
        )

        # Then
        assert len(figure.data) == 1

        # ---Main line plot checks---
        main_line_plot: plotly.graph_objects.Scatter = figure.data[0]

        # The main line should be drawn as a black `spline` plot
        main_line: plotly.graph_objects.scatter.Line = main_line_plot.line
        assert main_line.color == RGBAColours.BLACK.stringified
        assert main_line.shape == "spline"

        # The fill colour under the plot should be a dark grey
        assert main_line_plot.fillcolor == RGBAColours.LINE_DARK_GREY.stringified
```

In this example, we follow the same structure as if we were writing a unit test but we add more comments as necessary.

> Note that we consider something to be an integration test if there is some I/O bound activity. 
> Think request over network or database query.

Generally, test time can be a good indication 
and can tell us when we have not drawn the boundaries that we think we have. 

---

### Test directory structure

Generally the `tests/` directory should mirror the source code.
Let's say we wanted to write tests for a function in the following file:

```
cms/
  dashboard/
    management/
        commands/
            build_cms_site.py  # <- Our function to be tested lives within this file
```

In this case, we would add test files in the following locations:
```
cms/ 
  ...
tests/
  unit/
    cms/
      dashboard/
        management/
          commands/
            test_build_cms_site.py  # <- Unit tests against our function would live here
    ...
  integration/
    cms/
      dashboard/
        management/
          commands/
            test_build_cms_site.py   # <- Integration tests against our function would live here
```

---

## Common practices

### Raising errors instead of returning none

In general returning `None` is ill-advised for failure scenarios. 
Making defensive checks within a piece of code and returning `None` if some condition does not hold true is ambigious 
and imposes an additional burden on the caller.

For example:
```python
if identifier == 1:
    return "some_string"

return None
```

In this case, we should instead prefer to raise a custom error. 
```python
if identifier == 1:
    return "some_string"

raise InvalidIdentifierError()
```

This makes our intention clear and the caller will know immediately if they have a problem to deal with.

### Explicit signatures

Using `*args` and `**kwargs` in function/method signatures should be used sparingly.

```python
def get_geographies(*args, **kwargs):
    ...
```

Most of the time it is preferable to declare the arguments which are expected:
```python
def get_geographies(geography_type: str):
    ...
```

### Making calls with keyword arguments

For pieces of code under our control, we should always make calls with keyword arguments 
rather than positional arguments:

```python
get_metrics(geography_type, topic)
```
For example, the above would be brittle and can lead to subtle bugs.

Instead, we should prefer:
```python
get_metrics(geography_type=geography_type, topic=topic)
```

Unless there is a very good reason to do so, we should enforce the use of key word arguments by default:

```python
def get_metrics(*, geography_type: str, topic: str):
    ...
```

Note that the star (`*`) operator here forces the calling code 
to use key word arguments instead of positional arguments.

### Avoiding assert statements in source code

We shall avoid the use of `assert` statements in source code.

For Python processes, the application of th `assert` keyword can be easily switched off in production 
with the [PYTHONOPTIMIZE](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONOPTIMIZE) flag.
This is usually done for compilation optimization purposes.

As such, we prefer the use of custom exceptions over `assert` statements in source code.

---

## Standards

### Docstrings

We use the [Google Python docstring standard](https://google.github.io/styleguide/pyguide.html) for source code.

### Tickets > TODO comments

TODO comments tend to contribute to code rot.
We shall always favour writing a ticket for a follow-up piece of work 
instead of leaving a TODO comment in the source code.

---

## Tooling

Currently, the following tools are used and enforced within our CI/CD pipeline:

- `black`
- `ruff`
- `importlinter`
- `bandit`
- `pip-audit`

We intend to add `mypy` and other forms of static tooling in the future.