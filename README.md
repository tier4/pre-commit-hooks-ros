# pre-commit-hooks-ros

[ROS]-related hooks for [pre-commit]

## Usage

Write your `.pre-commit-config.yaml` as below.

```yaml
repos:
  - repo: https://github.com/tier4/pre-commit-hooks-ros
    rev: v0.7.0
    hooks:
      - id: flake8-ros
      - id: prettier-xacro
      - id: prettier-launch-xml
      - id: prettier-package-xml
      - id: ros-include-guard
      - id: sort-package-xml
```

## Hooks available

### flake8-ros

Apply [flake8] with the [ROS 2 settings](https://docs.ros.org/en/rolling/Installation/Ubuntu-Development-Setup.html#install-development-tools-and-ros-tools).

### prettier-xacro

Apply [Prettier] with [plugin-xml] to [xacro].

### prettier-launch-xml

Apply [Prettier] with [plugin-xml] to [launch.xml].

### prettier-package-xml

Apply [Prettier] with [plugin-xml] to [package.xml].

### ros-include-guard

Fix the macro name of include guards.

### sort-package-xml

Sort the dependent packages in [package.xml].
If you want to exclude a tag from sorting, add `<! -- no format -->` at the beginning of the line.

```xml
<!-- no format --> <depend>rclcpp</depend>
```

<!-- Links -->

[flake8]: https://github.com/PyCQA/flake8
[launch.xml]: https://design.ros2.org/articles/roslaunch_xml.html
[package.xml]: https://www.ros.org/reps/rep-0149.html
[plugin-xml]: https://github.com/prettier/plugin-xml/
[pre-commit]: https://github.com/pre-commit/pre-commit
[prettier]: https://prettier.io/
[ros]: https://ros.org/
[xacro]: http://wiki.ros.org/xacro
