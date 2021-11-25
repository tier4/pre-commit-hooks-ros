# pre-commit-hooks-ros

ros-related hooks for pre-commit <https://pre-commit.com/>

## Usage

Write your `.pre-commit-config.yaml` as below.

```yaml
repos:
  - repo: https://github.com/tier4/pre-commit-hooks-ros
    rev: v0.4.0
    hooks:
      - id: prettier-xacro-xml
      - id: prettier-launch-xml
      - id: prettier-package-xml
      - id: sort-package-xml
```

## Hooks available

### `prettier-xacro-xml`

Apply prettier to [xacro](http://wiki.ros.org/xacro).

### `prettier-launch-xml`

Apply prettier to launch.xml

### `prettier-package-xml`

Apply prettier to package.xml
### `sort-package-xml`

Sorts the names contained in each tag in package.xml.
If you want to exclude a tag from the sort, add `<! -- nolint -->` at the beginning of the line.

Example

```xml
<!-- nolint --> <depend>rclcpp</depend>
```
