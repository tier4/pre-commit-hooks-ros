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

### prettier-xacro-xml

Apply prettier to [xacro](http://wiki.ros.org/xacro).

### prettier-launch-xml

Apply prettier to [launch.xml](https://design.ros2.org/articles/roslaunch_xml.html).

### prettier-package-xml

Apply prettier to [package.xml](https://www.ros.org/reps/rep-0149.html).

### sort-package-xml

Sort the dependent packages in [package.xml](https://www.ros.org/reps/rep-0149.html).
If you want to exclude a tag from sorting, add `<! -- no format -->` at the beginning of the line.

```xml
<!-- no format --> <depend>rclcpp</depend>
```
